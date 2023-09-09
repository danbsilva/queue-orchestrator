from flask_restful import Api
from src.routes import serviceroutes, swaggerroutes, forwardrequestroutes

api = Api(prefix='/api')


def init_app(app):
    api.init_app(app)


# Swagger Routes
swaggerroutes.SwaggerRoute(api)

# Service Routes
serviceroutes.ServiceRoute(api)

# Forward Request
forwardrequestroutes.ForwardRequestRoute(api)


