from flask_restful import Api

from src import resources
from src.routes import automationroutes, steproutes, fieldroutes, itemroutes, swaggerroutes

api = Api(prefix='/automations')


def init_app(app):
    api.init_app(app)

# Swagger
#swaggerroutes.SwaggerRoutes(api)

# Endpoints for automations
automationroutes.AutomationRoutes(api)

# Endpoints for steps
#steproutes.StepRoutes(api)

# Endpoints for fields
#fieldroutes.FieldRoutes(api)

# Endpoints for items
#itemroutes.ItemRoutes(api)
