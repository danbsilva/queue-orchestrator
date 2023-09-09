from src import resources


class ItemRoutes:

    def __init__(self, api):

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


