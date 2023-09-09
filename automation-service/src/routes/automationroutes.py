from flask_restful import Api

from src import resources

api = Api(prefix='/automations')


def init_app(app):
    api.init_app(app)

# Swagger
api.add_resource(resources.SwaggerResource, '/swagger.json',
                    methods=['GET'])

# Endpoints for automations
api.add_resource(resources.AutomationsResource, '/',
                 methods=['POST', 'GET'])
api.add_resource(resources.AutomationResource, '/<automation_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])
api.add_resource(resources.AutomationMeResource, '/me/',
                 methods=['GET'])
api.add_resource(resources.OwnersByAutomationResource, '/<automation_uuid>/owners/',
                 methods=['POST', 'GET', 'DELETE'])

# Endpoints for steps
api.add_resource(resources.StepsResource, '/<automation_uuid>/steps/',
                 methods=['POST', 'GET'])
api.add_resource(resources.StepResource, '/steps/<step_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])

# Endpoints for fields
api.add_resource(resources.FieldsResource, '/steps/<step_uuid>/fields/',
                    methods=['POST', 'GET'])
api.add_resource(resources.FieldResource, '/steps/fields/<field_uuid>/',
                    methods=['GET', 'PATCH', 'DELETE'])


# Endpoints for items
api.add_resource(resources.ItemsByAutomationResource, '/<automation_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemResource, '/items/<item_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])
api.add_resource(resources.ItemsByStepResource, '/steps/<step_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemUpdateStatusResource, '/items/<item_uuid>/update-status/',
                 methods=['PATCH'])


# Endpoints for history
api.add_resource(resources.ItemHistoricResource, '/items/<item_uuid>/historic/',
                 methods=['GET'])
