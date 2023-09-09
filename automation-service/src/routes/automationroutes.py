from src.controllers.automationcontroller import (AutomationResource, AutomationsResource,
                                                  AutomationMeResource, OwnersByAutomationResource)


class AutomationRoutes:

    def __init__(self, api):

        # Endpoints for automations
        api.add_resource(AutomationsResource, '/',
                         methods=['POST', 'GET'])
        api.add_resource(AutomationResource, '/<automation_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])
        api.add_resource(AutomationMeResource, '/me/',
                         methods=['GET'])
        api.add_resource(OwnersByAutomationResource, '/<automation_uuid>/owners/',
                         methods=['POST', 'GET', 'DELETE'])


