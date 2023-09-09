from flask_restful import Resource
from src.docs import auth


__module_name__ = 'src.controllers.swaggercontroller'


class SwaggerResource(Resource):
    def get(self):
        return auth.doc_swagger
