from flask_restful import Resource

from src.docs import automations



__module_name__ = 'src.controllers.swaggercontroller'



## SWAGGER ##
class SwaggerResource(Resource):
    def get(self):
        return automations.doc_swagger