import base64
import re
from abc import ABCMeta

from six import string_types

from bigchaindb.crypto.iostream import base64_add_padding, base64_remove_padding

CONDITION_REGEX = r'^cc:1:[1-9a-f][0-9a-f]{0,2}:[a-zA-Z0-9_-]{43}:[1-9][0-9]{0,50}$'


class Condition(metaclass=ABCMeta):
    _bitmask = None
    _hash = None
    _max_fulfillment_length = None

    @staticmethod
    def from_uri(serialized_condition):
        """
        Create a Condition object from a URI.

        This method will parse a condition URI and construct a corresponding Condition object.

        Args:
            serialized_condition (str): URI representing the condition

        Returns:
            Condition: Resulting object
        """
        if not isinstance(serialized_condition, string_types):
            raise TypeError('Serialized condition must be a string')

        pieces = serialized_condition.split(':')
        if not pieces[0] == 'cc':
            raise ValueError('Serialized condition must start with "cc:"')

        if not pieces[1] == '1':
            raise ValueError('Condition must be version 1')

        if not re.match(CONDITION_REGEX, serialized_condition):
            raise ValueError('Invalid condition format')

        condition = Condition()
        condition.bitmask = int(pieces[2])
        condition.hash = base64.urlsafe_b64decode(base64_add_padding(pieces[3]))
        condition.max_fulfillment_length = int(pieces[4])

        return condition

    @property
    def bitmask(self):
        """
        Return the bitmask of this condition.

        For simple condition types this is simply the bit representing this type.
        For meta-conditions, these are the bits representing the types of the subconditions.

        Return:
            int: Bitmask corresponding to this condition.
        """
        return self._bitmask

    @bitmask.setter
    def bitmask(self, value):
        """
        Set the bitmask.

        Sets the required bitmask to validate a fulfillment for this condition.

        Args:
            value (int): representation of bitmask.
        """
        self._bitmask = value

    @property
    def hash(self):
        """
        Return the hash of the condition.

        A primary component of all conditions is the hash. It encodes the static
        properties of the condition. This method enables the conditions to be
        constant size, no matter how complex they actually are. The data used to
        generate the hash consists of all the static properties of the condition
        and is provided later as part of the fulfillment.

        Return:
            Hash of the condition
        """
        if not self._hash:
            raise ValueError
        return self._hash

    @hash.setter
    def hash(self, value):
        """
        Validate and set the hash of this condition.

        Typically conditions are generated from fulfillments and the hash is
        calculated automatically. However, sometimes it may be necessary to
        construct a condition URI from a known hash. This method enables that case.

        Args:
            value (Buffer): Hash as binary.
        """
        # TODO: value must be Buffer
        # if not isinstance(value, Buffer):
        #   raise ValueError
        self._hash = value

    @property
    def max_fulfillment_length(self):
        """
        Return the maximum fulfillment length.

        The maximum fulfillment length is the maximum allowed length for any
        fulfillment payload to fulfill this condition.

        The condition defines a maximum fulfillment length which all
        implementations will enforce. This allows implementations to verify that
        their local maximum fulfillment size is guaranteed to accomodate any
        possible fulfillment for this condition.

        Otherwise an attacker could craft a fulfillment which exceeds the maximum
        size of one implementation, but meets the maximum size of another, thereby
        violating the fundamental property that fulfillments are either valid
        everywhere or nowhere.

        Return:
             (int) Maximum length (in bytes) of any fulfillment payload that fulfills this condition..
        """
        if not self._max_fulfillment_length:
            raise ValueError
        return self._max_fulfillment_length

    @max_fulfillment_length.setter
    def max_fulfillment_length(self, value):
        """
        Set the maximum fulfillment length.

        The maximum fulfillment length is normally calculated automatically, when
        calling `Fulfillment#getCondition`. However, when

        Args:
             value (int): Maximum fulfillment payload length in bytes.
        """
        self._max_fulfillment_length = value

    def serialize_uri(self):
        """
        Generate the URI form encoding of this condition.

        Turns the condition into a URI containing only URL-safe characters. This
        format is convenient for passing around conditions in URLs, JSON and other text-based formats.

        Returns:
            string: Condition as a URI
        """

        return 'cc:1:{}:{}:{}'.format(self.bitmask,
                                      base64_remove_padding(
                                          base64.urlsafe_b64encode(self.hash)
                                      ).decode('utf-8'),
                                      self.max_fulfillment_length)
