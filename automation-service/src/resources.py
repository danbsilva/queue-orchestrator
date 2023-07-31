from decouple import config as config_env
from threading import Thread

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.extensions.flask_cache import cache

from src import schemas, logging
from src import kafka
from src import repository_automation, repository_automation_step, repository_automation_item, \
    repository_automation_item_history
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


# Function to format topic name
def format_topic_name(name):
    # Replace spaces with underscores
    name = name.replace(' ', '_')  # Replace spaces with underscores
    name = ''.join(
        e if e.isalnum() or e == '_' else '_' for e in name)  # Replace special characters with underscores
    name = name.upper()  # Convert to uppercase
    return name


def return_steps(automation, step=None):
    steps = repository_automation_step.get_steps_by_automation_id(automation_id=automation.id)
    max_step = len(steps)
    if step:
        current_step = list(filter(lambda x: x.step == step.step, steps))[0]
    else:
        current_step = steps[0]
    next_step = steps[current_step.step] if current_step.step < max_step else None

    json_steps = {
        "steps": {
            "max_steps": max_step,
            "current_step": current_step.to_json(),
            "next_step": next_step.to_json() if next_step else None
        }
    }

    return json_steps


def return_try_count(current_step):
    try_count = current_step.try_count if current_step.try_count else 1

    json_try_count = {
        "try_count": try_count
    }

    return json_try_count


def add_transaction_id_to_message():
    json_transaction_id = {
        "transaction_id": request.headers.get('X-TRANSACTION-ID')
    }

    return json_transaction_id


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


def verify_user_exists(user_uuid):
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


class SwaggerResource(Resource):
    def get(self):
        return automations.doc_swagger


# AUTOMATIONS ##
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
                return {'message': 'Error creating automation'}, 400

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    @cache.cached(timeout=60, query_string=True)
    def get():
        try:
            page, per_page, offset = get_page_args()

            automations = repository_automation.get_all()

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
    @cache.cached(timeout=60, query_string=True)
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

            try:
                automation = repository_automation.update(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                        f'Automation {automation.uuid} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.patch',
                                       f'Error updating automation: {e}')
                return {'message': 'Error updating automation'}, 400

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
                return {'message': 'Error deleting automation'}, 400

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

            message, status_code = verify_token()
            if status_code != 200:
                return {'message': message}, status_code

            user_uuid = message['user']['uuid']

            automations = repository_automation.get_by_owner(owner_uuid=user_uuid)

            if not automations:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationMeResource.get',
                                       f'Automations not found for user {user_uuid}')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

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

            schema_validate = validate_schema(schemas.OwnersPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owners_add = []
            owners_not_add = []
            for owner in data['owners']:
                response, code = verify_user_exists(owner['uuid'])
                if code != 200:
                    owners_not_add.append({'uuid': owner['uuid'], 'message': messages.USER_NOT_FOUND})
                else:
                    user = response['user']
                    if owner in automation.owners:
                        logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                               f'Owner {owner} already exists in automation {automation.uuid}')

                        owners_not_add.append({'uuid': owner['uuid'], 'message': messages.OWNER_ALREADY_EXISTS})

                    else:
                        owners_add.append(user)

            for owner in owners_add:
                try:
                    repository_automation.add_owners(automation, owner)
                    logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                            f'Owner {owner} added to automation {automation.uuid}')

                except Exception as e:
                    logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.post',
                                           f'Error adding owner {owner} to automation {automation.uuid}: {e}')

                    owners_not_add.append({'uuid': owner['uuid'], 'message': 'Error adding owner to automation'})
                    owners_add.remove(owner)

            return {'owners_success': owners_add,
                    'owners_fail': owners_not_add}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    @cache.cached(timeout=60, query_string=True)
    def get(automation_uuid):
        try:
            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            schema_owner = schemas.OwnersGetSchema()
            schema_data = schema_owner.dump(automation)

            logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                   f'Owners found for automation {automation_uuid}')
            return schema_data, 200

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

            schema_validate = validate_schema(schemas.OwnersDeleteSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'OwnerByAutomationResource.delete',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owners_remove = []
            owners_not_remove = []
            for owner in data['owners']:
                if owner not in automation.owners:
                    logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                           f'Owner {owner} not found in automation {automation.uuid}')

                    owners_not_remove.append({'uuid': owner['uuid'], 'message': messages.OWNER_NOT_FOUND})

                else:
                    owners_remove.append(owner)

            for owner in owners_remove:
                try:
                    repository_automation.remove_owners(automation, owner)
                    logging.send_log_kafka('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                            f'Owner {owner} removed from automation {automation.uuid}')
                except Exception as e:
                    logging.send_log_kafka('CRITICAL', __module_name__, 'OwnersByAutomationResource.delete',
                                           f'Error removing owner {owner} from automation {automation.uuid}: {e}')

                    owners_not_remove.append({'uuid': owner['uuid'], 'message': 'Error removing owner from automation'})
                    owners_remove.remove(owner)

            return {'owners_success': owners_remove,
                    'owners_fail': owners_not_remove}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'OwnerByAutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# STEPS ##
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

            schema_validate = validate_schema(schemas.AutomationStepPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            if repository_automation_step.get_by_name(data['name']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Step name {data["name"]} already exists')
                return {'message': messages.STEP_NAME_ALREADY_EXISTS}, 400

            if repository_automation_step.get_step_by_automation_id(automation.id, data['step']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Step {data["step"]} already exists for automation {automation_uuid}')
                return {'message': messages.STEP_ALREADY_EXISTS}, 400

            data['topic'] = format_topic_name(f'{automation.acronym} {data["topic"]}')

            if repository_automation_step.get_by_topic(data['topic']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Topic {data["topic"]} already exists')
                return {'message': messages.STEP_TOPIC_ALREADY_EXISTS}, 400

            try:
                automation_step = repository_automation_step.create(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                        f'Step {automation_step.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post',
                                       f'Error creating step: {e}')
                return {'message': 'Error creating step'}, 400

            kafka.create_topic(automation_step.topic, 1, 1)

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

            return {'step': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    @cache.cached(timeout=60, query_string=True)
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation = repository_automation.get_by_uuid(automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            automation_steps = repository_automation_step.get_all(automation)

            pagination_steps = automation_steps[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automation_steps))

            schema_automation_step = schemas.AutomationStepGetSchema(many=True)
            schema_data = schema_automation_step.dump(pagination_steps)

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
    @cache.cached(timeout=60, query_string=True)
    def get(step_uuid):
        try:
            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

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

            schema_validate = validate_schema(schemas.AutomationStepPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            try:
                automation_step = repository_automation_step.update(automation_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                        f'Step {automation_step.uuid} updated successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch',
                                       f'Error updating step: {e}')
                return {'message': 'Error updating step'}, 400

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

            return {'step': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(step_uuid):
        try:
            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            try:
                repository_automation_step.delete(automation_step)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                        f'Step {automation_step.uuid} deleted successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete',
                                       f'Error deleting step: {e}')
                return {'message': 'Error deleting step'}, 400

            kafka.delete_topic(automation_step.topic)
            return {'message': messages.STEP_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# ITEMS ##
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

            schema_validate = validate_schema(schemas.AutomationItemPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get steps
            steps = return_steps(automation)
            # Get current step
            current_step = repository_automation_step.get_step_by_automation_id(automation.id, 1)
            # Get try_count
            try_count = return_try_count(current_step)
            # Get transaction_id
            transaction_id = add_transaction_id_to_message()

            try:
                automation_item = repository_automation_item.create(automation, current_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                        f'Item {automation_item.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating item: {e}')
                return {'message':'Error creating item'}, 400

            try:
                repository_automation_item_history.create(automation_item=automation_item, description=messages.ITEM_CREATED)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            schema_automation_step_item = schemas.AutomationItemGetSchema()
            schema_data = schema_automation_step_item.dump(automation_item)

            schema_data.update(steps)  # Add steps to response
            schema_data.update(try_count)  # Add try_count to response
            schema_data.update(transaction_id)  # Add transaction_id to response

            Thread(target=kafka.kafka_producer, args=(current_step.topic, automation_item.uuid, schema_data,)).start()
            logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                   f'Item {schema_data["uuid"]} sent to Queue {current_step.topic}')

            try:
                repository_automation_item_history.create(automation_item=automation_item,
                                                        description=messages.ITEM_SENT_TO_QUEUE.format(current_step.topic))
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            del schema_data['transaction_id']  # Remove transaction_id from response
            return {'item': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    @cache.cached(timeout=60, query_string=True)
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            items = repository_automation_item.get_all_by_automation_id(automation_id=automation.id)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            schema_automation_step_item = schemas.AutomationItemWithoutStepsGetSchema(many=True)
            schema_data = schema_automation_step_item.dump(pagination_items)

            logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                   f'{str(len(pagination_items))} items found for automation {automation_uuid}')
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


class ItemResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    @cache.cached(timeout=60, query_string=True)
    def get(item_uuid):
        try:
            item = repository_automation_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            automation = repository_automation.get_by_id(id=item.automation_id)
            step = repository_automation_step.get_by_id(id=item.automation_step_id)

            # Get steps
            steps = return_steps(automation, step)
            # Get current step
            current_step = repository_automation_step.get_step_by_automation_id(automation.id, step.step)
            # Get try_count
            try_count = return_try_count(current_step)
            # Get transaction_id
            transaction_id = add_transaction_id_to_message()

            schema_automation_step_item = schemas.AutomationItemGetSchema()
            schema_data = schema_automation_step_item.dump(item)

            schema_data.update(steps)  # Add steps to response
            schema_data.update(try_count)  # Add try_count to response
            schema_data.update(transaction_id)  # Add transaction_id to response

            logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                   f'Item {schema_data["uuid"]} found')

            del schema_data['transaction_id']  # Remove transaction_id from response
            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.get', str(e))
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

            schema_validate = validate_schema(schemas.AutomationItemUpdateStatusPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            item = repository_automation_item.get_by_uuid(uuid=item_uuid)
            if not item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            if item.status == data['status']:
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} already with status {data["status"]}')
                return {'message': messages.ITEM_ALREADY_WITH_STATUS}, 200

            try:
                item.status = data['status']
                repository_automation_item.update_status(item)
                logging.send_log_kafka('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} updated for status {data["status"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error updating item {item_uuid}: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            try:
                repository_automation_item_history.create(automation_item=item, description=f'Item {data["status"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error creating history: {e}')

            schema_item = schemas.AutomationItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
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

            schema_validate = validate_schema(schemas.AutomationItemPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            automation = repository_automation.get_by_id(step.automation_id)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Automation {step.automation_id} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get steps
            steps = return_steps(automation, step)
            # Get try_count
            current_step = repository_automation_step.get_step_by_automation_id(automation.id, step.step)
            # Get try_count
            try_count = return_try_count(current_step)
            # Get transaction_id
            transaction_id = add_transaction_id_to_message()

            try:
                automation_item = repository_automation_item.create(automation, current_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                        f'Item {automation_item.uuid} created successfully')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating item: {e}')
                return {'message': 'Error creating item'}, 400

            try:
                repository_automation_item_history.create(automation_item=automation_item, description=messages.ITEM_CREATED)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating history: {e}')

            schema_automation_step_item = schemas.AutomationItemGetSchema()
            schema_data = schema_automation_step_item.dump(automation_item)

            schema_data.update(steps)
            schema_data.update(try_count)
            schema_data.update(transaction_id)

            Thread(target=kafka.kafka_producer, args=(current_step.topic, automation_item.uuid, schema_data, transaction_id,)).start()
            logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post', f'Item {schema_data["uuid"]} sent to Queue {current_step.topic}')

            try:
                repository_automation_item_history.create(automation_item=automation_item,
                                                          description=messages.ITEM_SENT_TO_QUEUE.format(current_step.topic))
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating history: {e}')

            return {'item': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()

            step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            automation_step_items = repository_automation_item.get_all_by_automation_step_id(automation_step_id=step.id)

            pagination_items = automation_step_items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automation_step_items))

            schema_automation_step_item = schemas.AutomationItemGetSchema(many=True)
            schema_data = schema_automation_step_item.dump(pagination_items)

            logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.get',
                                   f'{str(len(pagination_items))} items found for step {step_uuid}')
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


class ItemHistoryResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(item_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation_step_item = repository_automation_item.get_by_uuid(uuid=item_uuid)
            if not automation_step_item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemHistoryResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            automation_step_item_history = repository_automation_item_history.get_all_by_automation_item_id(automation_item_id=automation_step_item.id)

            pagination_item_history = automation_step_item_history[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automation_step_item_history))

            schema_automation_step_item_history = schemas.AutomationItemHistoryGetSchema(many=True)
            schema_data = schema_automation_step_item_history.dump(pagination_item_history)

            logging.send_log_kafka('INFO', __module_name__, 'ItemHistoryResource.get',
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
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemHistoryResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
