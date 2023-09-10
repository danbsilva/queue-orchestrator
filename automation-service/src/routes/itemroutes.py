from src.controllers.itemcontroller import ItemResource, ItemsByAutomationResource, ItemsByStepResource, ItemUpdateStatusResource, ItemHistoricResource


class ItemRoutes:

    def __init__(self, api):

        # Endpoints for items
        api.add_resource(ItemsByAutomationResource, '/<automation_uuid>/items/',
                         methods=['POST', 'GET'])
        api.add_resource(ItemResource, '/items/<item_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])
        api.add_resource(ItemsByStepResource, '/steps/<step_uuid>/items/',
                         methods=['POST', 'GET'])
        api.add_resource(ItemUpdateStatusResource, '/items/<item_uuid>/update-status/',
                         methods=['PATCH'])

        # Endpoints for history
        api.add_resource(ItemHistoricResource, '/items/<item_uuid>/historic/',
                         methods=['GET'])


