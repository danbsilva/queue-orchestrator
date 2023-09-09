import os
from src.logging import Logger

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError


from src import schemas
from src.models.servicemodel import ServiceModel
from src import messages
from werkzeug.exceptions import UnsupportedMediaType


__module_name__ = 'src.controllers.servicecontroller'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset


# Function to validate the schema
def validate_schema(schema, data):
    try:
        schema.load(data)
    except ValidationError as e:
        return e.messages


# Resource to create a new service
class ServicesResource(Resource):
    @staticmethod
    def post():
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServicePostSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.post',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = ServiceModel.get_by_service_name(service_name=data['service_name'])
            if service:
                return {'message': messages.SERVICE_NAME_ALREADY_REGISTERED}, 400

            try:
                service = ServiceModel.create(new_service=data)
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.post',
                                        f'Service created: {service.uuid}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ServicesResource.post',
                                        f'Error to create service: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.ServiceGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServicesResource.post', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def get():
        try:
            page, per_page, offset = get_page_args()

            services = ServiceModel.get_all()
            if not services:
                return {'message': messages.SERVICES_NOT_FOUND}, 404

            pagination_service = services[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(services))

            schema_service = schemas.ServiceGetSchema(many=True)
            schema_data = schema_service.dump(pagination_service)

            Logger().dispatch('INFO', __module_name__, 'ServicesResource.get', messages.SERVICES_LISTED_SUCCESSFULLY)

            return {'services': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_service),
                        'offset': offset
                    }}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServicesResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# Resource to create a new service
class ServiceResource(Resource):

    @staticmethod
    def get(service_uuid):
        try:
            service = ServiceModel.get_by_uuid(uuid=service_uuid)
            if not service:
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            schema_service = schemas.ServiceGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServiceResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def patch(service_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServicePatchSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = ServiceModel.get_by_uuid(uuid=service_uuid)
            if not service:
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch',
                                       messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            if data['service_name'] != service.service_name:
                service_name = ServiceModel.get_by_service_name(service_name=data['service_name'])
                if service_name:
                    Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch',
                                           messages.SERVICE_NAME_ALREADY_REGISTERED)
                    return {'message': messages.SERVICE_NAME_ALREADY_REGISTERED}, 400

            try:
                service = ServiceModel.update(service=service, new_service=data)
                Logger().dispatch('INFO', __module_name__, 'ServicesResource.patch',
                                       messages.SERVICE_UPDATED_SUCCESSFULLY)
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ServicesResource.patch',
                                       f'Error to update service: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.AutomationGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServicesResource.patch', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

