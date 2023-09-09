from src import resources


class AutomationRoutes:

    def __init__(self, api):

        # Endpoints for automations
        api.add_resource(resources.AutomationsResource, '/',
                         methods=['POST', 'GET'])
        api.add_resource(resources.AutomationResource, '/<automation_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])
        api.add_resource(resources.AutomationMeResource, '/me/',
                         methods=['GET'])
        api.add_resource(resources.OwnersByAutomationResource, '/<automation_uuid>/owners/',
                         methods=['POST', 'GET', 'DELETE'])


