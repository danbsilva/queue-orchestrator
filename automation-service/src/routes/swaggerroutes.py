from src import resources

class SwaggerRoutes:
    def __init__(self, api):
        api.add_resource(resources.SwaggerResource, '/swagger.json', methods=['GET'])
