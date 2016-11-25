from pytest import raises

from bigchaindb.common.exceptions import SchemaValidationError
from bigchaindb.common.schema import validate_vote_schema


def test_validate_vote(structurally_valid_vote):
    validate_vote_schema(structurally_valid_vote)


def test_validate_vote_fails():
    with raises(SchemaValidationError):
        validate_vote_schema({})
