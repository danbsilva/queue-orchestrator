from src.controllers.servicecontroller import ServicesResource


class RoutesServices:
    def __init__(self, api):
        api.add_resource(ServicesResource, '/services/', methods=['POST', 'GET'])


