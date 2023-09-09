from src.controllers.fowardrequestcontroller import ForwardRequestResource

class ForwardRequestRoute:

    def __init__(self, api):

        # ForwardRequest
        api.add_resource(ForwardRequestResource, '/<string:service_name>/', '/<string:service_name>/<path:path>',
                 methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'])
        