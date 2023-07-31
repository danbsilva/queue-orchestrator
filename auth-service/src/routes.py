from flask_restful import Api
from src import resources

api = Api(prefix='/auth')


def init_app(app):
    api.init_app(app)

# Swagger
api.add_resource(resources.SwaggerResource, '/swagger.json',
                    methods=['GET'])

# Users
api.add_resource(resources.UsersResource, '/users/',
                 methods=['POST', 'GET'])
api.add_resource(resources.UserResource, '/users/<user_uuid>/',
                 methods=['POST', 'GET', 'PATCH', 'DELETE'])

# Me
api.add_resource(resources.UserMeResource, '/users/me/',
                 methods=['GET', 'PATCH'])
api.add_resource(resources.UserMeChangePasswordResource, '/users/me/change-password/',
                 methods=['POST'])
api.add_resource(resources.UserChangeRoleResource, '/users/<user_uuid>/change-role/',
                methods=['POST'])

# Validate Token
api.add_resource(resources.ValidateTokenResource, '/validate/token/',
                    methods=['GET'])

# Validate Admin
api.add_resource(resources.ValidateAdminResource, '/validate/admin/',
                    methods=['GET'])

# Login/Logout
api.add_resource(resources.LoginResource, '/login/',
                 methods=['POST'])
api.add_resource(resources.LogoutResource, '/logout/',
                 methods=['GET'])

# Email Validation
api.add_resource(resources.SendEmailValidationResource, '/send-email-validation/',
                 methods=['POST'])
api.add_resource(resources.ValidateEmailResource, '/validate-email/<token>/',
                 methods=['GET'])

# Forgot Password
api.add_resource(resources.ForgotPasswordResource, '/forgot-password/',
                 methods=['POST'])
api.add_resource(resources.ResetPasswordResource, '/reset-password/<token>/',
                 methods=['GET'])
