from flask import current_app
from flask_restful import Resource

from bigchaindb.web.views.base import make_error


class ValidatorsApi(Resource):
    def get(self):
        """API endpoint to get validators set.

        Return:
            A JSON string containing the validator set of the current node.
        """

        pool = current_app.config['bigchain_pool']

        try:
            with pool() as bigchain:
                validators = bigchain.get_validators()

            return validators

        except:
            return make_error(500)
