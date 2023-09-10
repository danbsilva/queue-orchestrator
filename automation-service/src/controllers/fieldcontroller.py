import os
from marshmallow import ValidationError

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from werkzeug.exceptions import UnsupportedMediaType

from src.providers import cors_provider

from src.providers import cors_provider
from src.logging import Logger
from src.schemas import fieldschemas
from src.models.stepmodel import StepModel
from src.models.fieldmodel import FieldModel

from src import messages



__module_name__ = 'src.controllers.fieldcontroller'


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



# Function to format field name
def format_field_name(name):
    # Replace spaces with underscores
    name = name.replace(' ', '_')  # Replace spaces with underscores
    name = ''.join(
        e if e.isalnum() or e == '_' else '_' for e in name)  # Replace special characters with underscores

    name = name.lower()  # Convert to lowercase
    return name



## FIELDS ##
class FieldsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post(step_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(fieldschemas.FieldPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.post',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            data['name'] = format_field_name(data['name'])

            try:
                field = FieldModel.create(step, data)
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.post',
                                        f'Field {field.uuid} created successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'FieldsResource.post',
                                       f'Error creating field: {e}')
                return {'message': messages.ERROR_CREATING_FIELD}, 400

            schema_field = fieldschemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'FieldsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(step_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            step = StepModel.get_by_uuid(uuid=step_uuid)
            if not step:
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.get',
                                       f'Step {step_uuid} not found')
                return {'message': messages.STEP_NOT_FOUND}, 404

            try:
                fields = FieldModel.get_all(step=step, search=search)
                Logger().dispatch('INFO', __module_name__, 'FieldsResource.get',
                                        f'Fields of step {step.uuid} listed successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'FieldsResource.get',
                                       f'Error listing fields: {e}')
                return {'message': 'Error listing fields'}, 400

            pagination_fields = fields[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(fields))

            schema_field = fieldschemas.FieldGetSchema(many=True)
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
            Logger().dispatch('CRITICAL', __module_name__, 'FieldsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class FieldResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(field_uuid):
        try:
            field = FieldModel.get_by_uuid(uuid=field_uuid)
            if not field:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.get',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            schema_field = fieldschemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'FieldResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(field_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(fieldschemas.FieldPatchSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            field = FieldModel.get_by_uuid(uuid=field_uuid)
            if not field:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.patch',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            try:
                field = FieldModel.update(field, data)
                Logger().dispatch('INFO', __module_name__, 'FieldResource.patch',
                                        f'Field {field.uuid} updated successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'FieldResource.patch',
                                       f'Error updating field: {e}')
                return {'message': messages.ERROR_UPDATING_FIELD}, 400

            schema_field = fieldschemas.FieldGetSchema()
            schema_data = schema_field.dump(field)

            return {'field': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'FieldResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(field_uuid):
        try:
            field = FieldModel.get_by_uuid(uuid=field_uuid)
            if not field:
                Logger().dispatch('INFO', __module_name__, 'FieldResource.delete',
                                       f'Field {field_uuid} not found')
                return {'message': messages.FIELD_NOT_FOUND}, 404

            try:
                FieldModel.delete(field)
                Logger().dispatch('INFO', __module_name__, 'FieldResource.delete',
                                        f'Field {field.uuid} deleted successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'FieldResource.delete',
                                       f'Error deleting field: {e}')
                return {'message': messages.ERROR_DELETING_FIELD}, 400

            return {'message': messages.FIELD_DELETED}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'FieldResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

