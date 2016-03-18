from bigchaindb.crypto.condition import Condition
from bigchaindb.crypto.fulfillment import Fulfillment
from bigchaindb.crypto.fulfillments.base_sha256 import BaseSha256Fulfillment
from bigchaindb.crypto.buffer import Predictor, Reader, Writer


class ThresholdSha256Fulfillment(BaseSha256Fulfillment):
    _bitmask = 0x04

    def __init__(self):
        self._threshold = None

        self.subconditions = []
        self.subfulfillments = []

    def add_subcondition(self, subcondition):
        """
        Add a subcondition (unfulfilled).

        This can be used to generate a new threshold condition from a set of
        subconditions or to provide a non-fulfilled subcondition when creating a threshold fulfillment.

        Args:
            subcondition (Condition): Condition to add
        """
        if not isinstance(subcondition, Condition):
            raise TypeError('Subconditions must be objects of type Condition')
        self.subconditions.append(subcondition)

    def add_subfulfillment(self, subfulfillment):
        """
        Add a fulfilled subcondition.

        When constructing a threshold fulfillment, this method allows you to
        provide a fulfillment for one of the subconditions.

        Note that you do **not** have to add the subcondition if you're adding the
        fulfillment. The condition can be calculated from the fulfillment and will
        be added automatically.

        Args:
             subfulfillment (Fulfillment): Fulfillment to add
        """
        if not isinstance(subfulfillment, Fulfillment):
            raise TypeError('Subfulfillments must be objects of type Fulfillment')

        self.subfulfillments.append(subfulfillment)

    def get_all_subconditions(self):
        """
        Returns all subconditions including fulfilled ones.

        This method returns the subconditions plus all subfulfillments, converted to conditions.

        Returns:
            [Condition]: Set of subconditions
        """
        return self.subconditions + [f.condition for f in self.subfulfillments]

    @property
    def threshold(self):
        return self._threshold

    @threshold.setter
    def threshold(self, value):
        """
        Set the threshold.

        Determines the weighted threshold that is used to consider this condition
        fulfilled. If the added weight of all valid subfulfillments is greater or
        equal to this number, the threshold condition is considered to be fulfilled.

        Args:
            value (int): Integer threshold
        """
        self._threshold = value

    @property
    def bitmask(self):
        """
        Get full bitmask.

        This is a type of condition that can contain subconditions. A complete
        bitmask must contain the set of types that must be supported in order to
        validate this fulfillment. Therefore, we need to calculate the bitwise OR
        of this condition's TYPE_BIT and all subcondition's and subfulfillment's bitmasks.

        Returns:
             int: Complete bitmask for this fulfillment.
        """
        bitmask = self._bitmask

        for cond in self.subconditions:
            bitmask |= cond.bitmask

        for f in self.subfulfillments:
            bitmask |= f.bitmask

        return bitmask

    def write_hash_payload(self, hasher):
        """
        Produce the contents of the condition hash.

        This function is called internally by the `getCondition` method.

        HASH = SHA256(
            VARUINT TYPE_BIT
            VARUINT THRESHOLD
            VARARRAY
                VARUINT WEIGHT
                CONDITION
        )

        Args:
            hasher (Hasher): Hash generator
        """
        if not (len(self.subconditions) or len(self.subfulfillments)):
            raise ValueError('Requires subconditions')

        subconditions = [c.serialize_binary() for c in self.get_all_subconditions()]
        subconditions.sort(key=len)

        hasher.write_var_uint(ThresholdSha256Fulfillment()._bitmask)
        hasher.write_var_uint(self.threshold)
        hasher.write_var_uint(len(subconditions))
        for cond in subconditions:
            hasher.write(cond)
        return hasher

    def calculate_max_fulfillment_length(self):
        """
        Calculates the longest possible fulfillment length.

        In a threshold condition, the maximum length of the fulfillment depends on
        the maximum lengths of the fulfillments of the subconditions. However,
        usually not all subconditions must be fulfilled to meet the threshold. This
        means we only need to consider the worst case where the largest number of
        largest fulfillments are provided and the smaller fulfillments are not.

        The algorithm to calculate the worst case fulfillment size is not trivial,
        however, it does not need to provide the exact worst-case fulfillment
        length, only an upper bound for it.

        Return:
             int Maximum length of the fulfillment payload

        """
        # TODO: Currently wrong

        predictor = Predictor()

        # Calculate length of longest fulfillments
        max_fulfillments_length = [c.max_fulfillment_length for c in self.get_all_subconditions()]
        max_fulfillments_length.sort()
        worst_case_fulfillments_length = sum(max_fulfillments_length[-self.threshold:])

        predictor.write_var_uint(2)
        predictor.skip(worst_case_fulfillments_length)

        return predictor.size

    def parse_payload(self, reader):
        """
        Parse a fulfillment payload.

        Read a fulfillment payload from a Reader and populate this object with that fulfillment.

        Args:
            reader (Reader): Source to read the fulfillment payload from.
        """
        if not isinstance(reader, Reader):
            raise TypeError('reader must be a Reader instance')
        self.threshold = reader.read_var_uint()

        fulfillment_count = reader.read_var_uint()
        for i in range(fulfillment_count):
            # TODO: Read weights
            # const weight = 1
            reader.skip_var_uint()
            self.add_subfulfillment(Fulfillment.from_binary(reader))

        condition_count = reader.read_var_uint()
        for i in range(condition_count):
            # TODO: Read weights
            # const weight = 1
            reader.skip_var_uint()
            self.add_subcondition(Condition.from_binary(reader))

    def write_payload(self, writer):
        """
        Generate the fulfillment payload.

        This writes the fulfillment payload to a Writer.

        FULFILLMENT_PAYLOAD =
            VARUINT THRESHOLD
            VARARRAY
                VARUINT WEIGHT
                FULFILLMENT
            VARARRAY
                VARUINT WEIGHT
                CONDITION

        Args:
            writer (Writer): Subject for writing the fulfillment payload.
        """
        if not isinstance(writer, Writer):
            raise TypeError('writer must be a Writer instance')
        conditions = [c.serialize_binary() for c in self.subconditions]

        # Get as many fulfillments as possible
        fulfillments = [{'fulfillment': f, 'binary': f.serialize_binary()} for f in self.subfulfillments]

        # Prefer shorter fulfillments
        fulfillments.sort(key=lambda f: len(f['binary']))

        # Cut off unnecessary fulfillments
        if len(fulfillments) < self.threshold:
            raise ValueError('Not enough subfulfillments')

        while len(fulfillments) > self.threshold:
            # TODO: only for valid fulfillments?
            conditions.append(fulfillments.pop()['fulfillment'].condition.serialize_binary())

        writer.write_var_uint(self.threshold)

        writer.write_var_uint(len(fulfillments))
        for fulfillment in fulfillments:
            # TODO: Support custom weights
            writer.write_var_uint(1)
            writer.write(fulfillment['binary'])

        writer.write_var_uint(len(conditions))
        for condition in conditions:
            # TODO: Support custom weights
            writer.write_var_uint(1)
            writer.write(condition)

        return writer

    def validate(self):
        """
        Check whether this fulfillment meets all validation criteria.

        This will validate the subfulfillments and verify that there are enough
        subfulfillments to meet the threshold.

        Returns:
             boolean: Whether this fulfillment is valid.
        """
        validations = [f.validate() for f in self.subfulfillments]
        return len([v for v in validations]) >= self.threshold
