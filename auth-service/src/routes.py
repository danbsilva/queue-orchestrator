from flask_restful import Api
from src import resources

api = Api()


def init_app(app):
    api.init_app(app)


api.add_resource(resources.UsersResource, '/auth/users/',
                 methods=['POST', 'GET'])
api.add_resource(resources.UserResource, '/auth/users/<user_uuid>/',
                 methods=['POST', 'GET', 'PATCH', 'DELETE'])
api.add_resource(resources.UserMeResource, '/auth/users/me/', '/auth/users/me/change-password/',
                 methods=['GET', 'PATCH'])
api.add_resource(resources.LoginResource, '/auth/users/login/',
                 methods=['POST'])
api.add_resource(resources.LogoutResource, '/auth/users/logout/',
                 methods=['POST'])

api.add_resource(resources.SendEmailValidationResource, '/auth/users/send-email-validation/',
                 methods=['POST'])

api.add_resource(resources.ValidateEmailResource, '/auth/users/validate-email/<token>/',
                 methods=['GET'])

