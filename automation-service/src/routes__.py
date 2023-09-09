from flask_restful import Api

from src import resources

api = Api()


def init_app(app):
    api.init_app(app)

# Swagger
api.add_resource(resources.SwaggerResource, '/automations/swagger.json',
                    methods=['GET'])

# Endpoints for automations
api.add_resource(resources.AutomationsResource, '/automations/',
                 methods=['POST', 'GET'])
api.add_resource(resources.AutomationResource, '/automations/<automation_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])
api.add_resource(resources.AutomationMeResource, '/automations/me/',
                 methods=['GET'])
api.add_resource(resources.OwnersByAutomationResource, '/automations/<automation_uuid>/owners/',
                 methods=['POST', 'GET', 'DELETE'])

# Endpoints for steps
api.add_resource(resources.StepsResource, '/automations/<automation_uuid>/steps/',
                 methods=['POST', 'GET'])
api.add_resource(resources.StepResource, '/automations/steps/<step_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])

# Endpoints for fields
api.add_resource(resources.FieldsResource, '/automations/steps/<step_uuid>/fields/',
                    methods=['POST', 'GET'])
api.add_resource(resources.FieldResource, '/automations/steps/fields/<field_uuid>/',
                    methods=['GET', 'PATCH', 'DELETE'])


# Endpoints for items
api.add_resource(resources.ItemsByAutomationResource, '/automations/<automation_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemResource, '/automations/items/<item_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])
api.add_resource(resources.ItemsByStepResource, '/automations/steps/<step_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemUpdateStatusResource, '/automations/items/<item_uuid>/update-status/',
                 methods=['PATCH'])


# Endpoints for history
api.add_resource(resources.ItemHistoricResource, '/automations/items/<item_uuid>/historic/',
                 methods=['GET'])
