from flask_restful import Api
from src.routes import swaggerroutes, userroutes


api = Api(prefix='/auth')


def init_app(app):
    api.init_app(app)

swaggerroutes.SwaggerRoutes(api)
userroutes.UserRoutes(api)