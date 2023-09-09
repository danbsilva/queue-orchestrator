from decouple import config as config_env
from threading import Thread
from marshmallow import fields
from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.extensions.flask_cache import cache

from src import schemas, logging
from src import kafka
from src import repository_automation, repository_step, repository_item, \
    repository_item_historic, repository_field
from src import messages
from src.providers import cors_provider
from werkzeug.exceptions import UnsupportedMediaType
from src.docs import automations
import requests


__module_name__ = 'src.resources'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(config_env('PER_PAGE')), type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset


# Function to validate schema
def validate_schema(schema, data):
    try:
        schema.load(data)
    except ValidationError as e:
        return e.messages


# Return Dynamic Schema for validation fields from database to each step
def return_dynamic_schema(fields_from_db):
    schema = schemas.DynamicSchema()
    for field in fields_from_db:
        field_name = field.name
        field_alias = field.alias
        field_type = getattr(fields, field.type.capitalize())

        field_args = {}
        if field.required:
            field_args["required"] = True

        # Add validation if exists
        dynamic_field = field_type(**field_args)

        if field.required:
            dynamic_field.required = True
            dynamic_field.allow_none = False
            dynamic_field.allow_empty = False

            required_message = f'{messages.FIELD_ITEM_REQUIRED.format(field_alias.upper())}'
            if field.type == 'url':
                invalid_message = f'{messages.FIELD_ITEM_INVALID_URL.format(field_alias.upper())}'
            else:
                invalid_message = f'{messages.FIELD_ITEM_INVALID.format(field_alias.upper())}'

            dynamic_field.error_messages = {
                'required': required_message,
                'null': required_message,
                'empty': required_message,
                'invalid': invalid_message,
                'invalid_url': invalid_message,
                'validator_failed': invalid_message,
            }

        schema.fields[field_name] = dynamic_field
        schema.declared_fields[field_name] = dynamic_field
        schema.load_fields[field_name] = dynamic_field
        schema.dump_fields[field_name] = dynamic_field

    return schema


# Function to format topic name
def format_topic_name(name):
    # Replace spaces with underscores
    name = name.replace(' ', '_')  # Replace spaces with underscores
    name = ''.join(
        e if e.isalnum() or e == '_' else '_' for e in name)  # Replace special characters with underscores
    name = name.upper()  # Convert to uppercase
    return name


# Function to format field name
def format_field_name(name):
    # Replace spaces with underscores
    name = name.replace(' ', '_')  # Replace spaces with underscores
    name = ''.join(
        e if e.isalnum() or e == '_' else '_' for e in name)  # Replace special characters with underscores

    name = name.lower()  # Convert to lowercase
    return name


# Function to verify token
def verify_token():
    try:
        response = requests.request('GET', 'http://auth:80/auth/validate/token/',
                                    headers=request.headers)
        if response.status_code != 200:
            logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                   f'Error validating token: {response.text}')
            return messages.UNAUTHORIZED, 401
        return response.json(), 200

    except Exception as e:
        logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                               f'Error validating token: {e}')
        return messages.INTERNAL_SERVER_ERROR, 500


# Function to verify owner exists
def verify_owner_exists(user_uuid):
    try:
        response = requests.request('GET', f'http://auth:80/auth/users/{user_uuid}/',
                                    headers=request.headers)
        if response.status_code != 200:
            logging.send_log_kafka('INFO', __module_name__, 'verify_user_exists',
                                   f'Error validating user: {response.text}')
            return messages.UNAUTHORIZED, 401
        return response.json(), 200

    except Exception as e:
        logging.send_log_kafka('INFO', __module_name__, 'verify_user_exists',
                               f'Error validating user: {e}')
        return messages.INTERNAL_SERVER_ERROR, 500


## SWAGGER ##
class SwaggerResource(Resource):
    def get(self):
        return automations.doc_swagger


## AUTOMATIONS ##
class AutomationsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post():
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post',
                                       f'Error getting data: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_validate = validate_schema(schemas.AutomationPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if repository_automation.get_by_name(data['name']):
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation name {data["name"]} already exists')
                return {'message': messages.AUTOMATION_NAME_ALREADY_EXISTS}, 400

            if repository_automation.get_by_acronym(data['acronym']):
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation acronym {data["acronym"]} already exists')
                return {'message': messages.AUTOMATION_ACRONYM_ALREADY_EXISTS}, 400

            try:
                automation = repository_automation.create(data)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation {automation.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post',
                                       f'Error creating automation: {e}')
                return {'message': messages.ERROR_CREATING_AUTOMATION}, 400

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get():
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automations = repository_automation.get_all(search=search)

            pagination_automations = automations[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automations))

            schema_automation = schemas.AutomationGetSchema(many=True)
            schema_data = schema_automation.dump(pagination_automations)

            logging.send_log_kafka('INFO', __module_name__, 'AutomationsResource.get',
                                   f'{str(len(pagination_automations))} automations found')
            return {'automations': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_automations),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class AutomationResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.get',
                                   f'Automation {schema_data["uuid"]} found')
            return {'automation': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.AutomationPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            if data.get('name'):
                if automation.name != data['name']:
                    if repository_automation.get_by_name(data['name']):
                        logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                               f'Automation name {data["name"]} already exists')
                        return {'message': messages.AUTOMATION_NAME_ALREADY_EXISTS}, 400

            if data.get('acronym'):
                if automation.acronym != data['acronym']:
                    if repository_automation.get_by_acronym(data['acronym']):
                        logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                               f'Automation acronym {data["acronym"]} already exists')
                        return {'message': messages.AUTOMATION_ACRONYM_ALREADY_EXISTS}, 400

            try:
                automation = repository_automation.update(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                        f'Automation {automation.uuid} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.patch',
                                       f'Error updating automation: {e}')
                return {'message': messages.ERROR_UPDATING_AUTOMATION}, 400

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(automation_uuid):
        try:
            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.delete', f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            try:
                repository_automation.delete(automation)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.delete',
                                        f'Automation {automation.uuid} deleted successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.delete',
                                       f'Error deleting automation: {e}')
                return {'message': messages.ERROR_DELETING_AUTOMATION}, 400

            return {'message': messages.AUTOMATION_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class AutomationMeResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get():
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')
            message, status_code = verify_token()
            if status_code != 200:
                return {'message': message}, status_code

            user_uuid = message['user']['uuid']

            automations = repository_automation.get_by_owner(owner_uuid=user_uuid, search=search)

            pagination_automations = automations[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automations))

            schema_automation = schemas.AutomationGetSchema(many=True)
            schema_data = schema_automation.dump(pagination_automations)

            logging.send_log_kafka('INFO', __module_name__, 'AutomationMeResource.get',
                                   f'{str(len(pagination_automations))} automations found for user {user_uuid}')

            return  {'automations': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_automations),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationMeResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class OwnersByAutomationResource(Resource):

    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.OwnerPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owner = data
            response, code = verify_owner_exists(owner['uuid'])
            if code != 200:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Owner {owner["uuid"]} not found')
                return {'message': messages.OWNER_NOT_FOUND}, 404

            user = response['user']
            if owner["uuid"] in [owner_db['uuid'] for owner_db in automation.owners]:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Owner {owner["uuid"]} already exists in automation {automation.uuid}')

                return {'message': messages.OWNER_ALREADY_EXISTS}, 400

            try:
                repository_automation.add_owners(automation, user)
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                        f'Owner {owner["uuid"]} added to automation {automation.uuid}')

            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Error adding owner {owner["uuid"]} to automation {automation.uuid}: {e}')

            return {'owner': user}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owners = repository_automation.get_owners(automation_uuid=automation_uuid, search=search)

            pagination_owners = owners[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(owners))

            schema_data = owners

            logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                   f'Owners found for automation {automation_uuid}')
            return {'owners': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_owners),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.OwnerDeleteSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnerByAutomationResource.delete',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owner = data
            if owner['uuid'] not in [owner_db['uuid'] for owner_db in automation.owners]:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Owner {owner["uuid"]} not found in automation {automation.uuid}')
                return {'message': messages.OWNER_NOT_FOUND}, 404

            try:
                repository_automation.remove_owners(automation, owner)
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                        f'Owner {owner["uuid"]} removed from automation {automation.uuid}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Error removing owner {owner["uuid"]} from automation {automation.uuid}: {e}')

            return {'message': messages.OWNER_REMOVED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'OwnerByAutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


## STEPS ##
class StepsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.StepPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            if repository_step.get_by_name_and_automation_id(automation.id, data['name']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Step name {data["name"]} already exists')
                return {'message': messages.STEP_NAME_ALREADY_EXISTS}, 400

            if repository_step.get_step_by_automation_id(automation.id, data['step']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Step {data["step"]} already exists for automation {automation_uuid}')
                return {'message': messages.STEP_ALREADY_EXISTS}, 400

            data['topic'] = format_topic_name(f'{automation.acronym} {data["topic"]}')

            if repository_step.get_by_topic(data['topic']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Topic {data["topic"]} already exists')
                return {'message': messages.STEP_TOPIC_ALREADY_EXISTS}, 400

            try:
                step = repository_step.create(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                        f'Step {step.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post',
                                       f'Error creating step: {e}')
                return {'message': messages.ERROR_CREATING_STEP}, 400

            kafka.create_topic(step.topic, 1, 1)

            schema_step = schemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            return {'step': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automation = repository_automation.get_by_uuid(automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            steps = repository_step.get_all(automation.id, search=search)

            pagination_steps = steps[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(steps))

            schema_step = schemas.StepGetSchema(many=True)
            schema_data = schema_step.dump(pagination_steps)

            logging.send_log_kafka('INFO', __module_name__, 'StepsResource.get',
                                   f'{str(len(pagination_steps))} steps found for automation {automation_uuid}')
            return {'steps': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_steps),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class StepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            schema_step = schemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            logging.send_log_kafka('INFO', __module_name__, 'StepResource.get',
                                   f'Step {schema_data["uuid"]} found')
            return {'step': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.StepPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            if data.get('name'):
                if step.name != data['name']:
                    if repository_step.get_by_name_and_automation_id(step.automation.id, data['name']):
                        logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                               f'Step name {data["name"]} already exists')
                        return {'message': messages.STEP_NAME_ALREADY_EXISTS}, 400

            if data.get('step'):
                if step.step != data['step']:
                    if repository_step.get_step_by_automation_id(step.automation.id, data['step']):
                        logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                               f'Step {data["step"]} already exists for automation {step.automation.uuid}')
                        return {'message': messages.STEP_ALREADY_EXISTS}, 400

            if data.get('topic'):
                data['topic'] = format_topic_name(f'{step.automation.acronym} {data["topic"]}')
                if step.topic != data['topic']:
                    if repository_step.get_by_topic(data['topic']):
                        logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                               f'Topic {data["topic"]} already exists')
                        return {'message': messages.STEP_TOPIC_ALREADY_EXISTS}, 400

            old_topic = step.topic
            new_topic = data['topic']

            try:
                step = repository_step.update(step, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                        f'Step {step.uuid} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch',
                                       f'Error updating step: {e}')
                return {'message': messages.ERROR_UPDATING_STEP}, 400

            Thread(target=kafka.rename_topic, args=(old_topic, new_topic, request.headers.get('X-TRANSACTION-ID'))).start()

            schema_step = schemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            return {'step': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(step_uuid):
        try:
            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            fields = repository_field.get_all(step)
            for field in fields:
                try:
                    repository_field.delete(field)
                    logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                            f'Field {field.uuid} deleted successfully')
                except Exception as e:
                    logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete',
                                           f'Error deleting field {field.uuid}: {e}')

            try:
                repository_step.delete(step)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                        f'Step {step.uuid} deleted successfully')
            except Exception as e:
                logging.send_log_kafka('ERROR', __module_name__, 'StepResource.delete',
                                       f'Error deleting step: {e}')
                return {'message': messages.ERROR_DELETING_STEP}, 400

            Thread(target=kafka.delete_topic, args=(step.topic, request.headers.get('X-TRANSACTION-ID'))).start()

            return {'message': messages.STEP_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


## FIELDS ##
class FieldsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.FieldPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            data['name'] = format_field_name(data['name'])

            try:
                field = repository_field.create(step, data)
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.post',
                                        f'Field {field.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'FieldsResource.post',
                                       f'Error creating field: {e}')
                return {'message': messages.ERROR_CREATING_FIELD}, 400

            schema_field = schemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'FieldsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            try:
                fields = repository_field.get_all(step, search=search)
                logging.send_log_kafka('INFO', __module_name__, 'FieldsResource.get',
                                        f'Fields of step {step.uuid} listed successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'FieldsResource.get',
                                       f'Error listing fields: {e}')
                return {'message': 'Error listing fields'}, 400

            pagination_fields = fields[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(fields))

            schema_field = schemas.FieldGetSchema(many=True)
            schema_data = schema_field.dump(pagination_fields)

            return {'fields': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_fields),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'FieldsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class FieldResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(field_uuid):
        try:
            field = repository_field.get_by_uuid(uuid=field_uuid)
            if not field:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.get',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            schema_field = schemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'FieldResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(field_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(schemas.FieldPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            field = repository_field.get_by_uuid(uuid=field_uuid)
            if not field:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.patch',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            try:
                field = repository_field.update(field, data)
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.patch',
                                        f'Field {field.uuid} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'FieldResource.patch',
                                       f'Error updating field: {e}')
                return {'message': messages.ERROR_UPDATING_FIELD}, 400

            schema_field = schemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'FieldResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(field_uuid):
        try:
            field = repository_field.get_by_uuid(uuid=field_uuid)
            if not field:
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.delete',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            try:
                repository_field.delete(field)
                logging.send_log_kafka('INFO', __module_name__, 'FieldResource.delete',
                                        f'Field {field.uuid} deleted successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'FieldResource.delete',
                                       f'Error deleting field: {e}')
                return {'message': messages.ERROR_DELETING_FIELD}, 400

            return {'message': messages.FIELD_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'FieldResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


## ITEMS ##
class ItemsByAutomationResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(schemas.ItemPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get automation
            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get steps
            steps = repository_step.get_all(automation)
            if not steps:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Automation {automation_uuid} has no steps')
                return {'message': messages.AUTOMATION_HAS_NO_STEPS}, 400

            # Get first step by automation
            first_step = repository_step.get_step_by_automation_id(automation.id, 1)

            # Get fields to validate schema by step
            fields = repository_field.get_all(first_step)  # get all fields from current step
            schema = return_dynamic_schema(fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Create item
            try:
                item = repository_item.create(automation, first_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                        f'Item {item.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.ERROR_CREATING_ITEM}, 400

            # Create historic
            try:
                repository_item_historic.create(item=item, description=messages.ITEM_CREATED)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            # Send item to Queue with transaction_id
            schema_item_to_kafka = schemas.ItemGetSchema()
            schema_data_to_kafka = schema_item_to_kafka.dump(item)
            schema_data_to_kafka['transaction_id'] = request.headers.get('X-TRANSACTION-ID') if request.headers.get('X-TRANSACTION-ID') else None

            # Send item to Queue Kafka
            try:
                Thread(target=kafka.kafka_producer, args=(item.step.topic, item.uuid, schema_data_to_kafka,)).start()
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Item {item.uuid} sent to Queue {item.step.topic}')
                try:
                    repository_item_historic.create(item=item,
                                                   description=messages.ITEM_SENT_TO_QUEUE.format(item.step.topic))
                except Exception as e:
                    logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                           f'Error creating history: {e}')

            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error sending item {item.uuid} to Queue {item.step.topic}: {e}')

            # Send item to response
            schema_item = schemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get all items by automation
            items = repository_item.get_all_by_automation_id(automation_id=automation.id)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                   f'{str(len(pagination_items))} items found for automation {automation_uuid}')

            # Send items to response
            schema_item = schemas.ItemGetSchema(many=True)
            schema_data = schema_item.dump(pagination_items)

            return {'items': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_items),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemsByStepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(schemas.ItemPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get step
            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            # Get fields to validate schema by step
            fields = repository_field.get_all(step)  # get all fields from current step
            schema = return_dynamic_schema(fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Create item
            try:
                item = repository_item.create(step.automation, step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                        f'Item {item.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.ERROR_CREATING_ITEM}, 400

            # Create historic
            try:
                repository_item_historic.create(item=item, description=messages.ITEM_CREATED)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating history: {e}')

            # Send item to Queue with transaction_id
            schema_item_to_kafka = schemas.ItemGetSchema()
            schema_data_to_kafka = schema_item_to_kafka.dump(item)
            schema_data_to_kafka['transaction_id'] = request.headers.get('X-TRANSACTION-ID') if request.headers.get('X-TRANSACTION-ID') else None

            # Send item to Queue Kafka
            try:
                Thread(target=kafka.kafka_producer, args=(item.step.topic, item.uuid, schema_data_to_kafka,)).start()
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post', f'Item {item.uuid} sent to Queue {item.step.topic}')

                try:
                    repository_item_historic.create(item=item, description=messages.ITEM_SENT_TO_QUEUE.format(item.step.topic))
                except Exception as e:
                    logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                           f'Error creating history: {e}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error sending item {item.uuid} to Queue {item.step.topic}: {e}')


            # Send item to response
            schema_item = schemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            # Get step
            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            # Get all items by step
            items = repository_item.get_all_by_automation_step_id(step_id=step.id, search=search)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.get',
                                   f'{str(len(pagination_items))} items found for step {step_uuid}')

            # Send items to response
            schema_item = schemas.ItemWithoutStepsGetSchema(many=True)
            schema_data = schema_item.dump(pagination_items)

            return {'items': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_items),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(item_uuid):
        try:
            item = repository_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                   f'Item {item.uuid} found')

            schema_item = schemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(item_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(schemas.ItemPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get item
            item = repository_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            # Get fields to validate schema by step
            fields = repository_field.get_all(item.step)  # get all fields from current step
            schema = return_dynamic_schema(fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if item.status == 'running':
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} cannot be updated because it is running')
                return {'message': messages.ITEM_CANNOT_BE_UPDATED}, 400

            # Update item
            try:
                item = repository_item.update(item, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} updated')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.ERROR_UPDATING_ITEM}, 400

            # Create historic
            schema_item = schemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(item_uuid):
        try:
            item = repository_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            if item.status != 'pending' and item.status != 'error':
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} cannot be deleted because it is not pending or error')
                return {'message': messages.ITEM_CANNOT_BE_DELETED}, 400

            # Delete historic
            historic = repository_item_historic.get_all_by_item_id(item.id)
            if historic:
                for h in historic:
                    try:
                        repository_item_historic.delete(h)
                        logging.send_log_kafka('INFO', __module_name__, 'ItemResource.delete',
                                                  f'Item {item_uuid} history deleted')
                    except Exception as e:
                        logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
                        return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            # Delete item
            try:
                repository_item.delete(item)
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} deleted')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
                return {'message': messages.ERROR_DELETING_ITEM}, 400

            return {'message': messages.ITEM_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemsSearchByStepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            # Get step
            step = repository_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsSearchByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            # Get all items by automation
            items = repository_item.get_by_step_id_and_search(step_id=step.id, search=search)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            logging.send_log_kafka('INFO', __module_name__, 'ItemsSearchResource.get',
                                   f'{str(len(pagination_items))} items found')

            # Send items to response
            schema_item = schemas.ItemGetSchema(many=True)
            schema_data = schema_item.dump(pagination_items)

            return {'items': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_items),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsSearchResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500



class ItemUpdateStatusResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def patch(item_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(schemas.ItemUpdateStatusPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get item
            item = repository_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            # Update status
            if item.status == data['status']:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} already with status {data["status"]}')
                return {'message': messages.ITEM_ALREADY_WITH_STATUS}, 200

            try:
                item.status = data['status']
                repository_item.update_status(item)
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} updated for status {data["status"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error updating item {item_uuid}: {e}')
                return {'message': messages.ERROR_UPDATING_ITEM}, 400

            # Create historic
            try:
                repository_item_historic.create(item=item, description=f'Item {data["status"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error creating history: {e}')

            # Send item to response
            schema_item = schemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemHistoricResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(item_uuid):
        try:
            page, per_page, offset = get_page_args()

            item = repository_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemHistoricResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            item_history = repository_item_historic.get_all_by_item_id(item_id=item.id)
            if not item_history:
                logging.send_log_kafka('INFO', __module_name__, 'ItemHistoricResource.get',
                                       f'History not found for item {item_uuid}')
                return {'message': messages.ITEM_HISTORY_NOT_FOUND}, 404

            pagination_item_history = item_history[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(item_history))

            schema_item_history = schemas.ItemHistoricGetSchema(many=True)
            schema_data = schema_item_history.dump(pagination_item_history)

            logging.send_log_kafka('INFO', __module_name__, 'ItemHistoricResource.get',
                                   f'{str(len(pagination_item_history))} history found for item {item_uuid}')
            return {'history': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_item_history),
                        'offset': offset
                    }}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemHistoricResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
