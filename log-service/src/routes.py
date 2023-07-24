from flask_restful import Api

from src import resources

api = Api()


def init_app(app):
    api.init_app(app)


api.add_resource(resources.LogsServicesResource, '/logs/services/',
                 methods=['POST', 'GET'])

api.add_resource(resources.LogsRequestsResource, '/logs/requests/',
                 methods=['POST', 'GET'])