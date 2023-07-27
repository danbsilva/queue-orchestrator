from decouple import config as config_env
from threading import Thread

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from src.extensions.flask_cache import cache
from flask_paginate import Pagination

from src import schemas, logging
from src import kafka
from src import repository
from src import messages
from src.providers import token_provider
from src.providers import hash_provider
from werkzeug.exceptions import UnsupportedMediaType


__module_name__ = 'src.resources'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(config_env('PER_PAGE')), type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset


def validate_schema(schema, data):
    try:
        schema.load(data)
    except ValidationError as e:
        return e.messages


class UsersResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated):
        try:
            try:
                new_user = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'UsersResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'UsersResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserPostSchema(), new_user)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'UsersResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if repository.get_by_email(email=new_user['email']):
                logging.send_log_kafka('INFO', __module_name__, 'UsersResource.post',
                                       f'Email {new_user["email"]} already exists')
                return {'message': messages.EMAIL_ALREADY_EXISTS}, 400

            try:
                user = repository.create(new_user)
                logging.send_log_kafka('INFO', __module_name__, 'UsersResource.post',
                                       f'User {user.uuid} created successfully by {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'UsersResource.post', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            return {'user': user_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UsersResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated):
        try:
            page, per_page, offset = get_page_args()

            users = repository.get_all()

            pagination_users = users[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(users))

            users_schema = schemas.UserGetSchema(many=True)
            users_data = users_schema.dump(users)

            logging.send_log_kafka('INFO', __module_name__, 'UsersResource.get',
                                   f'Returning {len(users_data)} users')
            return {'users': users_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_users),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UsersResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class UserResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, user_uuid):
        try:
            user = repository.get_by_uuid(uuid=user_uuid)
            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.get',
                                       f'User {user_uuid} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            logging.send_log_kafka('INFO', __module_name__, 'UserResource.get',
                                   f'User {user_uuid} found')
            return {'user': user_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def patch(user_authenticated, user_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if 'email' in data and repository.get_by_email(email=data['email']):
                return {'message': messages.EMAIL_ALREADY_EXISTS}, 400

            if 'username' in data and repository.get_by_username(username=data['username']):
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch',
                                       f'User {user_uuid} already exists')
                return {'message': messages.USERNAME_ALREADY_EXISTS}, 400

            user = repository.get_by_uuid(uuid=user_uuid)

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch',
                                       f'User {user_uuid} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            try:
                repository.update(user, data)
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.patch',
                                       f'User {user_uuid} updated successfully by {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'UserResource.patch', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            return {'user': user_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def delete(user_authenticated, user_uuid):
        try:
            user = repository.get_by_uuid(uuid=user_uuid)
            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.delete',
                                       f'User {user_uuid} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            try:
                repository.delete(user)
                logging.send_log_kafka('INFO', __module_name__, 'UserResource.delete',
                                       f'User {user_uuid} deleted successfully by {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'UserResource.delete', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            return {'message': messages.USER_DELETED_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class UserMeResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated):
        try:
            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user_authenticated)

            logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.get',
                                   f'Returning user {user_authenticated["uuid"]}')
            return {'user': user_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserMeResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    def patch(user_authenticated):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if 'email' in data and repository.get_by_email(email=data['email']):
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                        f'Email {data["email"]} already exists')
                return {'message': messages.EMAIL_ALREADY_EXISTS}, 400

            if 'username' in data and repository.get_by_username(username=data['username']):
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'User {user_authenticated["uuid"]} already exists')
                return {'message': messages.USERNAME_ALREADY_EXISTS}, 400

            user = repository.get_by_uuid(uuid=user_authenticated['uuid'])

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'User {user_authenticated["uuid"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            try:
                repository.update(user, data)
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'User {user_authenticated["uuid"]} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            return {'user': user_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserMeResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class UserMeChangePasswordResource(Resource):
    @staticmethod
    @token_provider.verify_token
    def patch(user_authenticated):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserChangePasswordSchema(), data)

            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if data['new_password'] != data['confirm_new_password']:
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', 'Passwords not match')
                return {'message': messages.PASSWORDS_NOT_MATCH}, 400

            user = repository.get_by_uuid(uuid=user_authenticated['uuid'])
            if not hash_provider.check_password_hash(data['password'], user.password):
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch', 'Actual password not match')
                return {'message': messages.ACTUAL_PASSWORD_NOT_MATCH}, 400

            try:
                repository.change_password(user, data['new_password'])
                logging.send_log_kafka('INFO', __module_name__, 'UserMeResource.patch',
                                       f'User {user_authenticated["uuid"]} changed password successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'UserMeResource.patch', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            return {'message': messages.PASSWORD_CHANGED_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'UserMeResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class LoginResource(Resource):
    @staticmethod
    def post():
        try:
            try:
                user = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserLoginSchema(), user)

            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            user_db = repository.get_by_email(email=user['email'])

            if not user_db:
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post',
                                       f'User {user["email"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            if not user_db.email_valid:
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post',
                                       f'User {user["email"]} not validated')
                return {'message': messages.USER_NON_VALIDATED_EMAIL}, 400

            if not hash_provider.check_password_hash(user['password'], user_db.password):
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post',
                                       f'User {user["email"]} invalid credentials')
                return {'message': messages.INVALID_CREDENTIALS}, 400

            try:
                token = token_provider.create_token(payload=user_db.to_json())
                logging.send_log_kafka('INFO', __module_name__, 'LoginResource.post',
                                       f'User {user["email"]} logged in successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'LoginResource.post', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            return {'token': token}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'LoginResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class LogoutResource(Resource):
    @staticmethod
    @token_provider.verify_token
    def post(user_authenticated):
        try:
            token = request.headers['Authorization'].replace('Bearer ', '')
            cache.set(f'BLACKLIST_TOKEN_{token}', f'{token}')

            logging.send_log_kafka('INFO', __module_name__, 'LogoutResource.post',
                                   f'User {user_authenticated["uuid"]} logged out successfully')
            return {'message': messages.LOGOUT_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'LogoutResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ValidateTokenResource(Resource):

    @staticmethod
    @token_provider.verify_token
    def get(user_authenticated):
        try:
            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user_authenticated)

            logging.send_log_kafka('INFO', __module_name__, 'ValidateTokenResource.get',
                                   f'Token by {user_authenticated["uuid"]} is valid')
            return {'user': user_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ValidateTokenResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ValidateAdminResource(Resource):
        @staticmethod
        @token_provider.verify_token
        @token_provider.admin_required
        def get(user_authenticated):
            try:
                user_schema = schemas.UserGetSchema()
                user_data = user_schema.dump(user_authenticated)

                logging.send_log_kafka('INFO', __module_name__, 'ValidateAdminResource.get',
                                    f'User {user_authenticated["uuid"]} is admin')
                return {'user': user_data}, 200

            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ValidateAdminResource.get', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ForgotPasswordResource(Resource):
    @staticmethod
    def post():
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ForgotPasswordResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ForgotPasswordResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.ForgotPasswordSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ForgotPasswordResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            user = repository.get_by_email(email=data['email'])

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'ForgotPasswordResource.post',
                                       f'User {data["email"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            token = token_provider.create_token(payload={'email': user.email})
            url = f'{config_env("API_GATEWAY_HOST")}/auth/users/reset-password/{token}/'

            payload = {
                "transaction_id": request.headers.get('X-TRANSACTION-ID'),
                "email": data['email'],
                "subject": 'Recovey Password',
                "template": f"<html><body><a href='{url}'>Clique aqui</a></body></html>"
            }

            Thread(target=kafka.kafka_producer,
                   args=(config_env('TOPIC_SEND_EMAIL_RECOVERY_PASSWORD'), user.uuid, payload,)).start()

            logging.send_log_kafka('INFO', __module_name__, 'ForgotPasswordResource.post',
                                   f'Email sent topic {config_env("TOPIC_SEND_EMAIL_RECOVERY_PASSWORD")}')
            return {'message': messages.EMAIL_SENT_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ForgotPasswordResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ResetPasswordResource(Resource):
    @staticmethod
    def get(token):
        try:
            cache_token = cache.get(f'BLACKLIST_TOKEN_{token}')
            if cache_token:
                logging.send_log_kafka('INFO', __module_name__, 'ResetPasswordResource.get',
                                       f'Token {token} is blacklisted')
                return {'message': messages.TOKEN_IS_INVALID}, 401

            user_authenticated = token_provider.verify_token_email(token=token)
            if not user_authenticated:
                logging.send_log_kafka('INFO', __module_name__, 'ResetPasswordResource.get',
                                       f'Token {token} is invalid')
                return {'message': messages.TOKEN_IS_INVALID}, 401

            user = repository.get_by_email(email=user_authenticated['email'])

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'ResetPasswordResource.get',
                                       f'User {user_authenticated["email"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            if not user.email_valid:
                logging.send_log_kafka('INFO', __module_name__, 'ResetPasswordResource.get',
                                       f'User {user_authenticated["email"]} not validated')
                return {'message': messages.USER_NON_VALIDATED_EMAIL}, 400

            cache.set(f'BLACKLIST_TOKEN_{token}', token, timeout=60 * 60 * 24 * 7)

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            return {'message': messages.USER_VALIDATED_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ResetPasswordResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ValidateEmailResource(Resource):
    @staticmethod
    def get(token):
        try:
            cache_token = cache.get(f'BLACKLIST_TOKEN_{token}')
            if cache_token:
                logging.send_log_kafka('INFO', __module_name__, 'ValidateEmailResource.get',
                                       f'Token {token} is blacklisted')
                return {'message': messages.TOKEN_IS_INVALID}, 401

            user_authenticated = token_provider.verify_token_email(token=token)
            if not user_authenticated:
                logging.send_log_kafka('INFO', __module_name__, 'ValidateEmailResource.get',
                                       f'Token {token} is invalid')
                return {'message': messages.TOKEN_IS_INVALID}, 401

            user = repository.get_by_email(email=user_authenticated['email'])

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'ValidateEmailResource.get',
                                       f'User {user_authenticated["email"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            if user.email_valid:
                logging.send_log_kafka('INFO', __module_name__, 'ValidateEmailResource.get',
                                       f'User {user_authenticated["email"]} already validated')
                return {'message': messages.USER_ALREADY_VALIDATED}, 400

            try:
                repository.validate_email(user)
                logging.send_log_kafka('INFO', __module_name__, 'ValidateEmailResource.get',
                                       f'User {user_authenticated["email"]} validated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ValidateEmailResource.get', str(e))
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            cache.set(f'BLACKLIST_TOKEN_{token}', token, timeout=60 * 60 * 24 * 7)

            user_schema = schemas.UserGetSchema()
            user_data = user_schema.dump(user)

            return {'message': messages.USER_VALIDATED_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ValidateEmailResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class SendEmailValidationResource(Resource):
    @staticmethod
    def post():
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.UserSendEmailValidationSchema(), data)

            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            user = repository.get_by_email(email=data['email'])

            if not user:
                logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post',
                                       f'User {data["email"]} not found')
                return {'message': messages.USER_NOT_FOUND}, 404

            if user.email_valid:
                logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post',
                                       f'User {data["email"]} already validated')
                return {'message': messages.USER_ALREADY_VALIDATED}, 400

            token = token_provider.create_token(payload={'email': user.email})
            url = f'{config_env("API_GATEWAY_HOST")}/auth/users/validate-email/{token}/'

            payload = {
                "transaction_id": request.headers.get('X-TRANSACTION-ID'),
                "email": data['email'],
                "subject": 'Account Validation',
                "template": f"<html><body><a href='{url}'>Clique aqui</a></body></html>"
            }

            Thread(target=kafka.kafka_producer,
                   args=(config_env('TOPIC_SEND_EMAIL_VALIDATION_ACCOUNT'), user.uuid, payload,)).start()

            logging.send_log_kafka('INFO', __module_name__, 'SendEmailValidationResource.post',
                                   f'Email sent topic {config_env("TOPIC_SEND_EMAIL_VALIDATION_ACCOUNT")}')
            return {'message': messages.EMAIL_SENT_SUCCESSFULLY}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'SendEmailValidationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
