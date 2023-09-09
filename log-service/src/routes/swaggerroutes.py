from src.controllers.swaggercontroller import SwaggerResource


class RoutesSwagger:
    def __init__(self, api):
        api.add_resource(SwaggerResource, '/swagger.json', methods=['GET'])
