from flask_restful import Api
from src import resources

api = Api(prefix='/api')


def init_app(app):
    api.init_app(app)


api.add_resource(resources.ServicesResource, '/services/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ServiceResource, '/services/<service_uuid>/',
                 methods=['GET'])
api.add_resource(resources.ForwardRequestResource, '/<string:service_name>/', '/<string:service_name>/<path:path>',
                 methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])

