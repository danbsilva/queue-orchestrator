import os
from threading import Thread
from marshmallow import ValidationError
from marshmallow import fields

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from werkzeug.exceptions import UnsupportedMediaType

from src.providers import cors_provider

from src.providers import cors_provider
from src.logging import Logger
from src.services.kafkaservice import KafkaService
from src.schemas import itemschemas, fieldschemas
from src.models.automationmodel import AutomationModel
from src.models.stepmodel import StepModel
from src.models.itemmodel import ItemModel, ItemHistoricModel
from src.models.fieldmodel import FieldModel

from src import messages



__module_name__ = 'src.controllers.itemcontroller'


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


# Return Dynamic Schema for validation fields from database to each step
def return_dynamic_schema(fields_from_db):
    schema = fieldschemas.DynamicSchema()
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



## ITEMS ##
class ItemsByAutomationResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(itemschemas.ItemPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get automation
            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get steps
            steps = StepModel.get_all(automation_id=automation.id, search='')
            if not steps:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Automation {automation_uuid} has no steps')
                return {'message': messages.AUTOMATION_HAS_NO_STEPS}, 400

            # Get first step by automation
            first_step = StepModel.get_step_by_automation_id(automation_id=automation.id, step=1)

            # Get fields to validate schema by step
            fields = FieldModel.get_all(step=first_step, search='')  # get all fields from current step
            schema = return_dynamic_schema(fields_from_db=fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Create item
            try:
                item = ItemModel.create(automation=automation, first_step=first_step, new_item=data)
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                        f'Item {item.uuid} created successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.ERROR_CREATING_ITEM}, 400

            # Create historic
            try:
                ItemHistoricModel.create(item=item, description=messages.ITEM_CREATED)
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error creating history: {e}')

            # Send item to Queue with transaction_id
            schema_item_to_kafka = itemschemas.ItemGetSchema()
            schema_data_to_kafka = schema_item_to_kafka.dump(item)
            schema_data_to_kafka['transaction_id'] = request.headers.get('X-TRANSACTION-ID') if request.headers.get('X-TRANSACTION-ID') else None

            # Send item to Queue Kafka
            try:
                Thread(target=KafkaService().producer, args=(item.step.topic, item.uuid, schema_data_to_kafka,)).start()
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Item {item.uuid} sent to Queue {item.step.topic}')
                try:
                    ItemHistoricModel.create(item=item, description=messages.ITEM_SENT_TO_QUEUE.format(item.step.topic))
                except Exception as e:
                    Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                           f'Error creating history: {e}')

            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Error sending item {item.uuid} to Queue {item.step.topic}: {e}')

            # Send item to response
            schema_item = itemschemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            # Get all items by automation
            items = ItemModel.get_all_by_automation_id(automation_id=automation.id)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.get',
                                   f'{str(len(pagination_items))} items found for automation {automation_uuid}')

            # Send items to response
            schema_item = itemschemas.ItemGetSchema(many=True)
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
            Logger().dispatch('CRITICAL', __module_name__, 'ItemsByAutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemsByStepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(itemschemas.ItemPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get step
            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            automation = AutomationModel.get_by_id(step.automation_id)

            # Get fields to validate schema by step
            fields = FieldModel.get_all(step=step, search='')  # get all fields from current step
            schema = return_dynamic_schema(fields_from_db=fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Create item
            try:
                item = ItemModel.create(automation=automation, first_step=step, new_item=data)
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post',
                                        f'Item {item.uuid} created successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating item: {e}')
                return {'message': messages.ERROR_CREATING_ITEM}, 400

            # Create historic
            try:
                ItemHistoricModel.create(item=item, description=messages.ITEM_CREATED)
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error creating history: {e}')

            # Send item to Queue with transaction_id
            schema_item_to_kafka = itemschemas.ItemGetSchema()
            schema_data_to_kafka = schema_item_to_kafka.dump(item)
            schema_data_to_kafka['transaction_id'] = request.headers.get('X-TRANSACTION-ID') if request.headers.get('X-TRANSACTION-ID') else None

            # Send item to Queue Kafka
            try:
                Thread(target=KafkaService().producer, args=(item.step.topic, item.uuid, schema_data_to_kafka,)).start()
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.post', f'Item {item.uuid} sent to Queue {item.step.topic}')

                try:
                    ItemHistoricModel.create(item=item, description=messages.ITEM_SENT_TO_QUEUE.format(item.step.topic))
                except Exception as e:
                    Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                           f'Error creating history: {e}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.post',
                                       f'Error sending item {item.uuid} to Queue {item.step.topic}: {e}')


            # Send item to response
            schema_item = itemschemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            # Get step
            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            # Get all items by step
            items = ItemModel.get_all_by_automation_step_id(step_id=step.id, search=search)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            Logger().dispatch('INFO', __module_name__, 'ItemsByStepResource.get',
                                   f'{str(len(pagination_items))} items found for step {step_uuid}')

            # Send items to response
            schema_item = itemschemas.ItemWithoutStepsGetSchema(many=True)
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
            Logger().dispatch('CRITICAL', __module_name__, 'ItemsByStepResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(item_uuid):
        try:
            item = ItemModel.get_by_uuid(uuid=item_uuid)
            if not item:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            Logger().dispatch('INFO', __module_name__, 'ItemResource.get',
                                   f'Item {item.uuid} found')

            schema_item = itemschemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(item_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(itemschemas.ItemPatchSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get item
            item = ItemModel.get_by_uuid(uuid=item_uuid)
            if not item:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            # Get fields to validate schema by step
            fields = FieldModel.get_all(item.step)  # get all fields from current step
            schema = return_dynamic_schema(fields)  # return dynamic schema from fields
            schema_validate = validate_schema(schema, data['data'])  # validate data with dynamic schema
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemsByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if item.status == 'running':
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} cannot be updated because it is running')
                return {'message': messages.ITEM_CANNOT_BE_UPDATED}, 400

            # Update item
            try:
                item = ItemModel.update(item, data)
                Logger().dispatch('INFO', __module_name__, 'ItemResource.patch',
                                       f'Item {item_uuid} updated')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.patch', str(e))
                return {'message': messages.ERROR_UPDATING_ITEM}, 400

            # Create historic
            schema_item = itemschemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(item_uuid):
        try:
            item = ItemModel.get_by_uuid(uuid=item_uuid)
            if not item:
                Logger().dispatch('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            if item.status != 'pending' and item.status != 'error':
                Logger().dispatch('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} cannot be deleted because it is not pending or error')
                return {'message': messages.ITEM_CANNOT_BE_DELETED}, 400

            # Delete historic
            historic = ItemHistoricModel.get_all_by_item_id(item.id)
            if historic:
                for h in historic:
                    try:
                        ItemHistoricModel.delete(h)
                        Logger().dispatch('INFO', __module_name__, 'ItemResource.delete',
                                                  f'Item {item_uuid} history deleted')
                    except Exception as e:
                        Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
                        return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            # Delete item
            try:
                ItemModel.delete(item)
                Logger().dispatch('INFO', __module_name__, 'ItemResource.delete',
                                       f'Item {item_uuid} deleted')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
                return {'message': messages.ERROR_DELETING_ITEM}, 400

            return {'message': messages.ITEM_DELETED}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemsSearchByStepResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            # Get step
            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'ItemsSearchByStepResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            # Get all items by automation
            items = ItemModel.get_by_step_id_and_search(step_id=step.id, search=search)

            pagination_items = items[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(items))

            Logger().dispatch('INFO', __module_name__, 'ItemsSearchResource.get',
                                   f'{str(len(pagination_items))} items found')

            # Send items to response
            schema_item = itemschemas.ItemGetSchema(many=True)
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
            Logger().dispatch('CRITICAL', __module_name__, 'ItemsSearchResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500



class ItemUpdateStatusResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def patch(item_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            # Validate schema
            schema_validate = validate_schema(itemschemas.ItemUpdateStatusPatchSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            # Get item
            item = ItemModel.get_by_uuid(uuid=item_uuid)
            if not item:
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            # Update status
            if item.status == data['status']:
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} already with status {data["status"]}')
                return {'message': messages.ITEM_ALREADY_WITH_STATUS}, 200

            try:
                item.status = data['status']
                ItemModel.update_status(item)
                Logger().dispatch('INFO', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Item {item_uuid} updated for status {data["status"]}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error updating item {item_uuid}: {e}')
                return {'message': messages.ERROR_UPDATING_ITEM}, 400

            # Create historic
            try:
                ItemHistoricModel.create(item=item, description=f'Item {data["status"]}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch',
                                       f'Error creating history: {e}')

            # Send item to response
            schema_item = itemschemas.ItemGetSchema()
            schema_data = schema_item.dump(item)

            return {'item': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ItemUpdateStatusResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ItemHistoricResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(item_uuid):
        try:
            page, per_page, offset = get_page_args()

            item = ItemModel.get_by_uuid(uuid=item_uuid)
            if not item:
                Logger().dispatch('INFO', __module_name__, 'ItemHistoricResource.get',
                                       f'Item {item_uuid} not found')
                return {'message': messages.ITEM_NOT_FOUND}, 404

            item_history = ItemHistoricModel.get_all_by_item_id(item_id=item.id)
            if not item_history:
                Logger().dispatch('INFO', __module_name__, 'ItemHistoricResource.get',
                                       f'History not found for item {item_uuid}')
                return {'message': messages.ITEM_HISTORY_NOT_FOUND}, 404

            pagination_item_history = item_history[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(item_history))

            schema_item_history = itemschemas.ItemHistoricGetSchema(many=True)
            schema_data = schema_item_history.dump(pagination_item_history)

            Logger().dispatch('INFO', __module_name__, 'ItemHistoricResource.get',
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
            Logger().dispatch('CRITICAL', __module_name__, 'ItemHistoricResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
