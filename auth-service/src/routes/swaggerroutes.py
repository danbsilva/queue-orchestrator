from src.controllers.usercontroller import (UsersResource, UserResource, UserMeResource, 
                                            UserMeChangePasswordResource, UserChangeRoleResource, 
                                            ValidateTokenResource, ValidateAdminResource, LoginResource, 
                                            LogoutResource, SendEmailValidationResource, ValidateEmailResource, 
                                            ForgotPasswordResource, ResetPasswordResource)


class RoutesUsers:
    def __init__(self, api):
        
        # Users
        api.add_resource(UsersResource, '/users/',
                         methods=['POST', 'GET'])
        api.add_resource(UserResource, '/users/<user_uuid>/',
                         methods=['POST', 'GET', 'PATCH', 'DELETE'])

        # Me
        api.add_resource(UserMeResource, '/users/me/',
                         methods=['GET', 'PATCH'])
        api.add_resource(UserMeChangePasswordResource, '/users/me/change-password/',
                         methods=['POST'])
        api.add_resource(UserChangeRoleResource, '/users/<user_uuid>/change-role/',
                         methods=['POST'])

        # Validate Token
        api.add_resource(ValidateTokenResource, '/validate/token/',
                         methods=['GET'])

        # Validate Admin
        api.add_resource(ValidateAdminResource, '/validate/admin/',
                         methods=['GET'])

        # Login/Logout
        api.add_resource(LoginResource, '/login/',
                         methods=['POST'])
        api.add_resource(LogoutResource, '/logout/',
                         methods=['GET'])

        # Email Validation
        api.add_resource(SendEmailValidationResource, '/send-email-validation/',
                         methods=['POST'])
        api.add_resource(ValidateEmailResource, '/validate-email/<token>/',
                         methods=['GET'])

        # Forgot Password
        api.add_resource(ForgotPasswordResource, '/forgot-password/',
                         methods=['POST'])
        api.add_resource(ResetPasswordResource, '/reset-password/<token>/',
                         methods=['GET'])
