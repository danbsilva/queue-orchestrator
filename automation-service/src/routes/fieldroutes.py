from src.controllers.fieldcontroller import FieldResource, FieldsResource


class FieldRoutes:

    def __init__(self, api):

        # Endpoints for fields
        api.add_resource(FieldsResource, '/steps/<step_uuid>/fields/',
                         methods=['POST', 'GET'])
        api.add_resource(FieldResource, '/steps/fields/<field_uuid>/',
                         methods=['GET', 'PATCH', 'DELETE'])


