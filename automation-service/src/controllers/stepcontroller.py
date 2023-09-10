import os
from threading import Thread

from marshmallow import ValidationError

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from werkzeug.exceptions import UnsupportedMediaType

from src.providers import cors_provider

from src.providers import cors_provider
from src.logging import Logger
from src.schemas import stepschemas
from src.models.stepmodel import StepModel
from src.models.automationmodel import AutomationModel
from src.models.fieldmodel import FieldModel

from src.services.kafkaservice import KafkaService
from src import messages



__module_name__ = 'src.controllers.stepcontroller'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
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



## STEPS ##
class StepsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(stepschemas.StepPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            if StepModel.get_by_name_and_automation_id(automation_id=automation.id, name=data['name']):
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                       f'Step name {data["name"]} already exists')
                return {'message': messages.STEP_NAME_ALREADY_EXISTS}, 400

            if StepModel.get_step_by_automation_id(automation_id=automation.id, step=data['step']):
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                       f'Step {data["step"]} already exists for automation {automation_uuid}')
                return {'message': messages.STEP_ALREADY_EXISTS}, 400

            data['topic'] = format_topic_name(name=f'{automation.acronym} {data["topic"]}')

            if StepModel.get_by_topic(topic=data['topic']):
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                       f'Topic {data["topic"]} already exists')
                return {'message': messages.STEP_TOPIC_ALREADY_EXISTS}, 400

            try:
                step = StepModel.create(automation=automation, new_step=data)
                Logger().dispatch('INFO', __module_name__, 'StepsResource.post',
                                        f'Step {step.uuid} created successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'StepsResource.post',
                                       f'Error creating step: {e}')
                return {'message': messages.ERROR_CREATING_STEP}, 400

            KafkaService().create_topic(topic_name=step.topic, num_partitions=3, replication_factor=1, transaction_id=request.headers.get('X-TRANSACTION-ID'))

            schema_step = stepschemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            return {'step': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'StepsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'StepsResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            steps = StepModel.get_all(automation.id, search)

            pagination_steps = steps[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(steps))

            schema_step = stepschemas.StepGetSchema(many=True)
            schema_data = schema_step.dump(pagination_steps)

            Logger().dispatch('INFO', __module_name__, 'StepsResource.get',
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
            Logger().dispatch('CRITICAL', __module_name__, 'StepsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class StepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            step = StepModel.get_by_uuid(step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'StepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            schema_step = stepschemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            Logger().dispatch('INFO', __module_name__, 'StepResource.get',
                                   f'Step {schema_data["uuid"]} found')
            return {'step': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'StepResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'StepResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'StepResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(stepschemas.StepPatchSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = StepModel.get_by_uuid(step_uuid)
            automation = AutomationModel.get_by_id(step.automation_id)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            if data.get('name'):
                if step.name != data['name']:
                    if StepModel.get_by_name_and_automation_id(automation_id=automation.id, name=data['name']):
                        Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                               f'Step name {data["name"]} already exists')
                        return {'message': messages.STEP_NAME_ALREADY_EXISTS}, 400

            if data.get('step'):
                if step.step != data['step']:
                    if StepModel.get_step_by_automation_id(automation_id=automation.id, step=data['step']):
                        Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                               f'Step {data["step"]} already exists for automation {automation.uuid}')
                        return {'message': messages.STEP_ALREADY_EXISTS}, 400

            if data.get('topic'):
                data['topic'] = format_topic_name(f'{automation.acronym} {data["topic"]}')
                if step.topic != data['topic']:
                    if StepModel.get_by_topic(topic=data['topic']):
                        Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                               f'Topic {data["topic"]} already exists')
                        return {'message': messages.STEP_TOPIC_ALREADY_EXISTS}, 400

            old_topic = step.topic
            new_topic = data['topic']

            try:
                step = StepModel.update(step=step, new_step=data)
                Logger().dispatch('INFO', __module_name__, 'StepResource.patch',
                                        f'Step {step.uuid} updated successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'StepResource.patch',
                                       f'Error updating step: {e}')
                return {'message': messages.ERROR_UPDATING_STEP}, 400

            Thread(target=KafkaService().rename_topic, args=(old_topic, new_topic, request.headers.get('X-TRANSACTION-ID'))).start()

            schema_step = stepschemas.StepGetSchema()
            schema_data = schema_step.dump(step)

            return {'step': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'StepResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(step_uuid):
        try:
            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'StepResource.delete',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            fields = FieldModel.get_all(step=step)
            for field in fields:
                try:
                    FieldModel.delete(field=field)
                    Logger().dispatch('INFO', __module_name__, 'StepResource.delete',
                                            f'Field {field.uuid} deleted successfully')
                except Exception as e:
                    Logger().dispatch('CRITICAL', __module_name__, 'StepResource.delete',
                                           f'Error deleting field {field.uuid}: {e}')

            try:
                StepModel.delete(step=step)
                Logger().dispatch('INFO', __module_name__, 'StepResource.delete',
                                        f'Step {step.uuid} deleted successfully')
            except Exception as e:
                Logger().dispatch('ERROR', __module_name__, 'StepResource.delete',
                                       f'Error deleting step: {e}')
                return {'message': messages.ERROR_DELETING_STEP}, 400

            Thread(target=KafkaService().delete_topic, args=(step.topic, request.headers.get('X-TRANSACTION-ID'))).start()

            return {'message': messages.STEP_DELETED}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'StepResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500