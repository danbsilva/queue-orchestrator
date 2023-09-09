from src.controllers.requestcontroller import RequestsResource


class RequestRoutes:
    def __init__(self, api):
        api.add_resource(RequestsResource, '/requests/', methods=['POST', 'GET'])
