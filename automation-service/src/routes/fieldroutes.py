from src import resources


class FieldRoutes:

    def __init__(self, api):

        # Endpoints for fields
        api.add_resource(resources.FieldsResource, '/steps/<step_uuid>/fields/',
                         methods=['POST', 'GET'])
        api.add_resource(resources.FieldResource, '/steps/fields/<field_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])


