import os
from src.logging import Logger

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError


from src import schemas
from src.models.routemodel import RouteModel
from src.models.servicemodel import ServiceModel
from src import messages
from werkzeug.exceptions import UnsupportedMediaType


__module_name__ = 'src.controllers.routecontroller'


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



class RoutesResource(Resource):
    @staticmethod
    def post(service_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServiceRoutePostSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = ServiceModel.get_by_uuid(uuid=service_uuid)
            if not service:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post',
                                            messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            route = RouteModel.get_by_route(route=data['route'])
            if route:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post',
                                            messages.SERVICE_ROUTE_ALREADY_REGISTERED)
                return {'message': messages.SERVICE_ROUTE_ALREADY_REGISTERED}, 400

            try:
                service_route = RouteModel.create(service=service, new_route=data)
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.post',
                                        messages.SERVICE_ROUTE_CREATED_SUCCESSFULLY)
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ServiceRoutesResource.post',
                                        f'Error to create service route: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.ServiceRouteGetSchema()
            schema_data = schema_service.dump(service_route)

            return {'route': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServiceRoutesResource.post', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def get(service_uuid):
        try:
            page, per_page, offset = get_page_args()

            service = ServiceModel.get_by_uuid(uuid=service_uuid)
            if not service:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.get',
                                            messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            routes = RouteModel.get_by_service_id(service_id=service.id)
            if not routes:
                Logger().dispatch('INFO', __module_name__, 'ServiceRoutesResource.get',
                                            messages.SERVICE_ROUTE_NOT_FOUND)
                return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

            pagination_route = routes[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(routes))

            schema_service = schemas.ServiceRouteGetSchema(many=True)
            schema_data = schema_service.dump(pagination_route)

            return {'routes': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_route),
                        'offset': offset
                    }}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServiceRoutesResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class RouteResource(Resource):
    @staticmethod
    def get(route_uuid):
        try:
            route = RouteModel.get_by_uuid(uuid=route_uuid)
            if not route:
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.get',
                                            messages.SERVICE_ROUTE_NOT_FOUND)
                return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

            schema_service = schemas.ServiceRouteGetSchema()
            schema_data = schema_service.dump(route)

            return {'route': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ServiceRouteResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def patch(route_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_route = schemas.ServiceRoutePatchSchema()
            schema_validate = validate_schema(schema=schema_route, data=data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            route = RouteModel.get_by_uuid(uuid=route_uuid)
            if not route:
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch',
                                            messages.SERVICE_ROUTE_NOT_FOUND)
                return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

            if 'route' in data:
                if route.route != data['route']:
                    route = RouteModel.get_by_route(route=data['route'])
                    if route:
                        Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch',
                                                    messages.SERVICE_ROUTE_ALREADY_REGISTERED)
                        return {'message': messages.SERVICE_ROUTE_ALREADY_REGISTERED}, 400

            try:
                route = RouteModel.update(route=route, new_route=data)
                Logger().dispatch('INFO', __module_name__, 'ServiceRouteResource.patch',
                                        messages.SERVICE_ROUTE_UPDATED_SUCCESSFULLY)
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'ServiceRouteResource.patch',
                                        f'Error to update service route: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_route = schemas.ServiceRouteGetSchema()
            schema_data = schema_route.dump(route)

            return {'route': schema_data}, 200

        except Exception as e:

            Logger().dispatch('CRITICAL', __module_name__, 'ServiceRouteResource.patch', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
