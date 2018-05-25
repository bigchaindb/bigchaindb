
class TransactionalElection(object):

    version = '0.0'
    name = 'base-class'

    def __init__(self):
        pass

    def propose(self, election_object):
        """Initiate a new election"""

        raise NotImplementedError

    def list(self, election_id):
        """List the election with id `election_id`"""

        raise NotImplementedError

    def is_valid_proposal(self, election_object):
        """Check if the `election_object` is a valid election"""

        raise NotImplementedError

    def vote(self, election_id, node_key_path):
        """Vote on the given `election_id`"""

        raise NotImplementedError

    def is_valid_vote(self, vote):
        """Validate the casted vote"""

        raise NotImplementedError

    def is_concluded(self, election_id, current_votes=[]):
        """Check if the Election with `election_id` has reached consensus"""

        raise NotImplementedError
