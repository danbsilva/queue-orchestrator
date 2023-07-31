from flask_restful import Api
from src import resources

api = Api(prefix='/api')


def init_app(app):
    api.init_app(app)

# Services
api.add_resource(resources.ServicesResource, '/services/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ServiceResource, '/services/<service_uuid>/',
                 methods=['GET', 'PATCH'])

# Service Routes
api.add_resource(resources.ServiceRoutesResource, '/services/<service_uuid>/routes/',
                    methods=['POST', 'GET'])
api.add_resource(resources.ServiceRouteResource, '/services/routes/<route_uuid>/',
                    methods=['GET', 'PATCH'])

# Forward Request
api.add_resource(resources.ForwardRequestResource, '/<string:service_name>/', '/<string:service_name>/<path:path>',
                 methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])

# Swagger
api.add_resource(resources.SwaggerResource, '/swagger.json', methods=['GET'], endpoint='swagger')
api.add_resource(resources.SwaggerUIResource, '/docs/', methods=['GET'])

