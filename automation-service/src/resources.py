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
from src.providers import token_provider

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


# AUTOMATIONS ##
class AutomationsResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated):
        try:
            data = request.get_json()
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
                                       f'Automation {automation.uuid} created successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post',
                                       f'Error creating automation: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated):
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
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, automation_uuid):
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
    @token_provider.verify_token
    @token_provider.admin_required
    def patch(user_authenticated, uuid):
        try:
            data = request.get_json()
            schema_validate = validate_schema(schemas.AutomationPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = repository_automation.get_by_uuid(uuid=uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Automation {uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            try:
                automation = repository_automation.update(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.patch',
                                        f'Automation {automation.uuid} updated successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.patch',
                                       f'Error updating automation: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_automation = schemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def delete(user_authenticated, automation_uuid):
        try:
            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.delete', f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            try:
                repository_automation.delete(automation)
                logging.send_log_kafka('INFO', __module_name__, 'AutomationResource.delete',
                                        f'Automation {automation.uuid} deleted successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.delete',
                                       f'Error deleting automation: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            return {'message': messages.AUTOMATION_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class AutomationMeResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated):
        try:
            page, per_page, offset = get_page_args()

            automations = repository_automation.get_by_owner(owner_uuid=user_authenticated['uuid'])
            if not automations:
                logging.send_log_kafka('INFO', __module_name__, 'AutomationMeResource.get',
                                       f'Automations not found for user {user_authenticated["uuid"]}')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            pagination_automations = automations[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automations))

            schema_automation = schemas.AutomationGetSchema(many=True)
            schema_data = schema_automation.dump(pagination_automations)

            logging.send_log_kafka('INFO', __module_name__, 'AutomationMeResource.get',
                                   f'{str(len(pagination_automations))} automations found for user {user_authenticated["uuid"]}')
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
            logging.send_log_kafka('CRITICAL', __module_name__, 'AutomationMeResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class OwnersByAutomationResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, automation_uuid):
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


# STEPS ##
class StepsResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated, automation_uuid):
        try:
            data = request.get_json()
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
                return {'message': messages.AUTOMATION_STEP_NAME_ALREADY_EXISTS}, 400

            if repository_automation_step.get_step_by_automation_id(automation.id, data['step']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Step {data["step"]} already exists for automation {automation_uuid}')
                return {'message': messages.AUTOMATION_STEP_ALREADY_EXISTS}, 400

            data['topic'] = format_topic_name(f'{automation.acronym} {data["topic"]}')

            if repository_automation_step.get_by_topic(data['topic']):
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                       f'Topic {data["topic"]} already exists')
                return {'message': messages.AUTOMATION_STEP_TOPIC_ALREADY_EXISTS}, 400

            try:
                automation_step = repository_automation_step.create(automation, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepsResource.post',
                                        f'Step {automation_step.uuid} created successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post',
                                       f'Error creating step: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            kafka.create_topic(automation_step.topic, 1, 1)

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

            return {'step': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, automation_uuid):
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
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, step_uuid):
        try:
            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_NOT_FOUND}, 404

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

            logging.send_log_kafka('INFO', __module_name__, 'StepResource.get',
                                   f'Step {schema_data["uuid"]} found')
            return {'step': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def patch(user_authenticated, step_uuid):
        try:
            data = request.get_json()
            schema_validate = validate_schema(schemas.AutomationStepPatchSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                       f'Step {step_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_NOT_FOUND}, 404

            try:
                automation_step = repository_automation_step.update(automation_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.patch',
                                        f'Step {automation_step.uuid} updated successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch',
                                       f'Error updating step: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_automation_step = schemas.AutomationStepGetSchema()
            schema_data = schema_automation_step.dump(automation_step)

            return {'step': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def delete(user_authenticated, step_uuid):
        try:
            automation_step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not automation_step:
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                       f'Step {step_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_NOT_FOUND}, 404

            try:
                repository_automation_step.delete(automation_step)
                logging.send_log_kafka('INFO', __module_name__, 'StepResource.delete',
                                        f'Step {automation_step.uuid} deleted successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete',
                                       f'Error deleting step: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            kafka.delete_topic(automation_step.topic)

            return {'message': messages.AUTOMATION_STEP_DELETED}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'StepResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# AUTOMATION ITEMS ##
class ItemsByAutomationResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated, automation_uuid):
        try:
            data = request.get_json()
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

            steps = return_steps(automation)
            current_step = repository_automation_step.get_step_by_automation_id(automation.id, 1)

            try_count = return_try_count(current_step)

            transaction_id = add_transaction_id_to_message()

            data['status'] = 'Pending'

            try:
                automation_item = repository_automation_item.create(automation, current_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                        f'Item {automation_item.uuid} created successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            try:
                repository_automation_item_history.create(automation_item=automation_item, description=messages.ITEM_CREATED)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            schema_automation_step_item = schemas.AutomationItemGetSchema()
            schema_data = schema_automation_step_item.dump(automation_item)

            schema_data.update(steps)
            schema_data.update(try_count)
            schema_data.update(transaction_id)

            Thread(target=kafka.kafka_producer, args=(current_step.topic, automation_item.uuid, schema_data,)).start()
            logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                   f'Item {schema_data["uuid"]} sent to Queue {current_step.topic}')

            try:
                repository_automation_item_history.create(automation_item=automation_item,
                                                        description=messages.ITEM_SENT_TO_QUEUE.format(current_step.topic))
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            return {'item': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, automation_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation = repository_automation.get_by_uuid(uuid=automation_uuid)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            automation_step_items = repository_automation_item.get_all_by_automation_id(automation_id=automation.id)

            pagination_items = automation_step_items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automation_step_items))

            schema_automation_step_item = schemas.AutomationStepItemGetSchema(many=True)
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
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated, item_uuid):
        try:
            automation_step_item = repository_automation_item.get_by_uuid(uuid=item_uuid)
            if not automation_step_item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_ITEM_NOT_FOUND}, 404

            schema_automation_step_item = schemas.AutomationStepItemGetSchema()
            schema_data = schema_automation_step_item.dump(automation_step_item)

            logging.send_log_kafka('INFO', __module_name__, 'ItemResource.get',
                                   f'Item {schema_data["uuid"]} found')
            return {'item': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ItemResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemsByStepResource(Resource):
    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated, step_uuid):
        try:
            data = request.get_json()
            schema_validate = validate_schema(schemas.AutomationItemPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_NOT_FOUND}, 404

            automation = repository_automation.get_by_id(step.automation_id)
            if not automation:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Automation {step.automation_id} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            steps = return_steps(automation, step)
            current_step = repository_automation_step.get_step_by_automation_id(automation.id, step.step)

            try_count = return_try_count(current_step)

            transaction_id = add_transaction_id_to_message()

            data['status'] = 'Pending'
            try:
                automation_item = repository_automation_item.create(automation, current_step, data)
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.post',
                                        f'Item {automation_item.uuid} created successfully by user {user_authenticated["uuid"]}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

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
    @token_provider.verify_token
    @token_provider.admin_required
    def get(user_authenticated, step_uuid):
        try:
            page, per_page, offset = get_page_args()

            step = repository_automation_step.get_by_uuid(uuid=step_uuid)
            if not step:
                logging.send_log_kafka('INFO', __module_name__, 'ItemsByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_NOT_FOUND}, 404

            automation_step_items = repository_automation_item.get_all_by_automation_step_id(automation_step_id=step.id)

            pagination_items = automation_step_items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automation_step_items))

            schema_automation_step_item = schemas.AutomationStepItemGetSchema(many=True)
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
    @token_provider.verify_token
    @token_provider.admin_required
    def get(user_authenticated, item_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation_step_item = repository_automation_item.get_by_uuid(uuid=item_uuid)
            if not automation_step_item:
                logging.send_log_kafka('INFO', __module_name__, 'ItemHistoryResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.AUTOMATION_STEP_ITEM_NOT_FOUND}, 404

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
