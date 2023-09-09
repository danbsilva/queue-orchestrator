from src.controllers.requestcontroller import RequestsResource


class RoutesRequests:
    def __init__(self, api):
        api.add_resource(RequestsResource, '/requests/', methods=['POST', 'GET'])
