from flask import current_app, Blueprint
from flask_restful import reqparse, Resource, Api


unspent_views = Blueprint('unspent_views', __name__)
unspent_api = Api(unspent_views)


class UnspentListApi(Resource):
    def get(self):
        """API endpoint to retrieve a list of links to transactions's
        conditions that have not been used in any previous transaction.

            Returns:
                A :obj:`list` of :cls:`str` of links to unfulfilled conditions.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('public_key', type=str, location='args',
                            required=True)
        args = parser.parse_args()

        pool = current_app.config['bigchain_pool']

        with pool() as bigchain:
            unspents = bigchain.get_owned_ids(args['public_key'])
            # NOTE: We pass '..' as a path to create a valid relative URI
            return [u.to_uri('..') for u in unspents]


unspent_api.add_resource(UnspentListApi,
                         '/unspents/',
                         strict_slashes=False)
