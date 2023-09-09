from src.controllers.servicecontroller import ServicesResource, ServiceResource

class ServiceRoute:

    def __init__(self, api):

        # Services
        api.add_resource(ServicesResource, '/services/',
                        methods=['POST', 'GET'])
        api.add_resource(ServiceResource, '/services/<service_uuid>/',
                        methods=['GET', 'PATCH'])
        