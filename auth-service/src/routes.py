from flask_restful import Api
from src import resources

api = Api()


def init_app(app):
    api.init_app(app)

# Users
api.add_resource(resources.UsersResource, '/auth/users/',
                 methods=['POST', 'GET'])
api.add_resource(resources.UserResource, '/auth/users/<user_uuid>/',
                 methods=['POST', 'GET', 'PATCH', 'DELETE'])

# Me
api.add_resource(resources.UserMeResource, '/auth/users/me/',
                 methods=['GET', 'PATCH'])
api.add_resource(resources.UserMeChangePasswordResource, '/auth/users/me/change-password/',
                 methods=['POST'])

# Validate Token
api.add_resource(resources.ValidateTokenResource, '/auth/token/validate/',
                    methods=['GET'])

# Validate Admin
api.add_resource(resources.ValidateAdminResource, '/auth/admin/validate/',
                    methods=['GET'])

# Login/Logout
api.add_resource(resources.LoginResource, '/auth/users/login/',
                 methods=['POST'])
api.add_resource(resources.LogoutResource, '/auth/users/logout/',
                 methods=['POST'])

# Email Validation
api.add_resource(resources.SendEmailValidationResource, '/auth/users/send-email-validation/',
                 methods=['POST'])
api.add_resource(resources.ValidateEmailResource, '/auth/users/validate-email/<token>/',
                 methods=['GET'])

# Forgot Password
api.add_resource(resources.ForgotPasswordResource, '/auth/users/forgot-password/',
                 methods=['POST'])
api.add_resource(resources.ResetPasswordResource, '/auth/users/reset-password/<token>/',
                 methods=['GET'])
