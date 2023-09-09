from src.controllers.servicecontroller import ServicesResource


class ServiceRoutes:
    def __init__(self, api):
        api.add_resource(ServicesResource, '/services/', methods=['POST', 'GET'])


