from flask_restful import Api
from src.routes import swaggerroutes, serviceroutes, requestroutes


api = Api(prefix='/logs')


def init_app(app):
    api.init_app(app)

swaggerroutes.SwaggerRoutes(api)
serviceroutes.ServiceRoutes(api)
requestroutes.RequestRoutes(api)