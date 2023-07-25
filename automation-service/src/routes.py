from flask_restful import Api

from src import resources

api = Api()


def init_app(app):
    api.init_app(app)

# Endpoints for automations
api.add_resource(resources.AutomationsResource, '/automations/',
                 methods=['POST', 'GET'])
api.add_resource(resources.AutomationResource, '/automations/<automation_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])
api.add_resource(resources.AutomationMeResource, '/automations/me/',
                 methods=['POST', 'GET'])
api.add_resource(resources.OwnersByAutomationResource, '/automations/<automation_uuid>/owners/',
                 methods=['GET'])

# Endpoints for steps
api.add_resource(resources.StepsResource, '/automations/<automation_uuid>/steps/',
                 methods=['POST', 'GET'])
api.add_resource(resources.StepResource, '/automations/steps/<step_uuid>/',
                 methods=['GET', 'PATCH', 'DELETE'])


# Endpoints for items
api.add_resource(resources.ItemsByAutomationResource, '/automations/<automation_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemResource, '/automations/items/<item_uuid>/',
                 methods=['GET', 'DELETE'])
api.add_resource(resources.ItemsByStepResource, '/automations/step/<step_uuid>/items/',
                 methods=['POST', 'GET'])
api.add_resource(resources.ItemInProcessResource, '/automations/items/<item_uuid>/in-process/',
                 methods=['PATCH'])


# Endpoints for history
api.add_resource(resources.ItemHistoryResource, '/automations/items/<item_uuid>/history/',
                    methods=['POST', 'GET'])
