from src.controllers.swaggercontroller import SwaggerResource, SwaggerUIResource

class SwaggerRoute:

    def __init__(self, api):

        # Swagger
        api.add_resource(SwaggerResource, '/swagger.json', methods=['GET'], endpoint='swagger')
        api.add_resource(SwaggerUIResource, '/docs/', methods=['GET'])
        