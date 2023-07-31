import re
from decouple import config as config_env
from src import logging

import requests
from flask import Response, request, jsonify, make_response, render_template
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.extensions.flask_cache import cache

from src import schemas, kafka
from src import repository_service, repository_service_routes, repository_service_documentations
from src import messages
from src.providers import token_provider
from werkzeug.exceptions import UnsupportedMediaType
import pprint


__module_name__ = 'src.resources'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(config_env('PER_PAGE')), type=int)
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
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServicePostSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.post',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = repository_service.get_by_service_name(service_name=data['service_name'])
            if service:
                return {'message': messages.SERVICE_NAME_ALREADY_REGISTERED}, 400

            try:
                service = repository_service.create(new_service=data)
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.post',
                                        f'Service created: {service.uuid}')
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ServicesResource.post',
                                        f'Error to create service: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.ServiceGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServicesResource.post', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cache.cached(timeout=60, query_string=True)
    def get():
        try:
            page, per_page, offset = get_page_args()

            services = repository_service.get_all()
            if not services:
                return {'message': messages.SERVICES_NOT_FOUND}, 404

            pagination_service = services[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(services))

            schema_service = schemas.ServiceGetSchema(many=True)
            schema_data = schema_service.dump(pagination_service)

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
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServicesResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# Resource to create a new service
class ServiceResource(Resource):

    @staticmethod
    @cache.cached(timeout=60, query_string=True)
    def get(service_uuid):
        try:
            service = repository_service.get_by_uuid(uuid=service_uuid)
            if not service:
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            schema_service = schemas.ServiceGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def patch(service_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServicePatchSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = repository_service.get_by_uuid(uuid=service_uuid)
            if not service:
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch',
                                       messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            if data['service_name'] != service.service_name:
                service_name = repository_service.get_by_service_name(service_name=data['service_name'])
                if service_name:
                    logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch',
                                           messages.SERVICE_NAME_ALREADY_REGISTERED)
                    return {'message': messages.SERVICE_NAME_ALREADY_REGISTERED}, 400

            try:
                service = repository_service.update(service=service, new_service=data)
                logging.send_log_kafka('INFO', __module_name__, 'ServicesResource.patch',
                                       messages.SERVICE_UPDATED_SUCCESSFULLY)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ServicesResource.patch',
                                       f'Error to update service: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.AutomationGetSchema()
            schema_data = schema_service.dump(service)

            return {'service': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServicesResource.patch', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ServiceRoutesResource(Resource):
    @staticmethod
    def post(service_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_service = schemas.ServiceRoutePostSchema()
            schema_validate = validate_schema(schema=schema_service, data=data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            service = repository_service.get_by_uuid(uuid=service_uuid)
            if not service:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post',
                                            messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            route = repository_service_routes.get_by_route(route=data['route'])
            if route:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post',
                                            messages.SERVICE_ROUTE_ALREADY_REGISTERED)
                return {'message': messages.SERVICE_ROUTE_ALREADY_REGISTERED}, 400

            try:
                service_route = repository_service_routes.create(service=service, new_service_route=data)
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.post',
                                        messages.SERVICE_ROUTE_CREATED_SUCCESSFULLY)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRoutesResource.post',
                                        f'Error to create service route: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_service = schemas.ServiceRouteGetSchema()
            schema_data = schema_service.dump(service_route)

            return {'route': schema_data}, 201

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRoutesResource.post', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cache.cached(timeout=60, query_string=True)
    def get(service_uuid):
        try:
            page, per_page, offset = get_page_args()

            service = repository_service.get_by_uuid(uuid=service_uuid)
            if not service:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.get',
                                            messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            routes = repository_service_routes.get_by_service_id(service_id=service.id)
            if not routes:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRoutesResource.get',
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
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRoutesResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class ServiceRouteResource(Resource):
    @staticmethod
    def get(route_uuid):
        try:
            route = repository_service_routes.get_by_uuid(uuid=route_uuid)
            if not route:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.get',
                                            messages.SERVICE_ROUTE_NOT_FOUND)
                return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

            schema_service = schemas.ServiceRouteGetSchema()
            schema_data = schema_service.dump(route)

            return {'route': schema_data}, 200

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRouteResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    def patch(route_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_route = schemas.ServiceRoutePatchSchema()
            schema_validate = validate_schema(schema=schema_route, data=data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch',
                                         f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            route = repository_service_routes.get_by_uuid(uuid=route_uuid)
            if not route:
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch',
                                            messages.SERVICE_ROUTE_NOT_FOUND)
                return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

            if 'route' in data:
                if route.route != data['route']:
                    route = repository_service_routes.get_by_route(route=data['route'])
                    if route:
                        logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch',
                                                    messages.SERVICE_ROUTE_ALREADY_REGISTERED)
                        return {'message': messages.SERVICE_ROUTE_ALREADY_REGISTERED}, 400

            try:
                route = repository_service_routes.update(service_route=route, new_service_route=data)
                logging.send_log_kafka('INFO', __module_name__, 'ServiceRouteResource.patch',
                                        messages.SERVICE_ROUTE_UPDATED_SUCCESSFULLY)
            except Exception as e:
                logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRouteResource.patch',
                                        f'Error to update service route: {e.args[0]}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_route = schemas.ServiceRouteGetSchema()
            schema_data = schema_route.dump(route)

            return {'route': schema_data}, 200

        except Exception as e:

            logging.send_log_kafka('CRITICAL', __module_name__, 'ServiceRouteResource.patch', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


# Resource to forward requests to microservices
class ForwardRequestResource(Resource):
    @staticmethod
    def dispatch_request(service_name, path=None, **kwargs):
        try:
            # Verify if the service is registered
            service = repository_service.get_by_service_name(service_name=service_name)

            # if the service is not registered, return 404
            if not service:
                logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                       messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            if not service.service_status:
                logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                       messages.SERVICE_UNAVAILABLE)
                return {'message': messages.SERVICE_UNAVAILABLE}, 503

            # Verify if the service is active
            routes = repository_service_routes.get_by_service_id(service_id=service.id)

            # Validate if the service has routes
            for route in routes:

                endpoint = f'{route.route}'.replace(f'/{service.service_name}/', '')
                args = f'<{route.args}>' if route.args else ''

                # patterns to validate the URL
                pattern_id = r'[0-9]+'  # pattern to validate ID
                pattern_uuid = r'[a-f0-9-]+'  # pattern to validate UUID
                pattern_jwt = r'[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+'  # pattern to validate JWT

                if args:  # if the route has arguments, the URL must be in the pattern
                    pattern = endpoint.replace(args, f'({pattern_uuid}|{pattern_jwt} |{pattern_id})')
                else:  # if the route has no arguments, the URL must be exactly the same
                    pattern = endpoint

                if path:  # if path is not None, add '/' to the end of the URL
                    if not path.endswith('/'):  # if the URL does not start with '/', add it
                        path += '/'

                # if the URL is in the pattern of a route, forward the request
                if re.fullmatch(pattern, path or ''):

                    # verify if the route requires authentication
                    if route.required_auth:
                        token_validation = token_provider.token_required()  # validate the token
                        if token_validation[1] >= 400:  # if the token is invalid, return the error
                            logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                    token_validation[0]['message'])
                            return token_validation[0], token_validation[1]

                    # verify if the route requires admin
                    if route.required_admin:
                        admin_validation = token_provider.admin_required()  # validate if the user is admin
                        if admin_validation[1] >= 400:  # if the user is not admin, return 401
                            logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                    admin_validation[0]['message'])
                            return admin_validation[0], admin_validation[1]

                    # Verify if the method is allowed
                    for method in route.methods_allowed:
                        if request.method in method:
                            break
                    else:
                        logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               messages.METHOD_NOT_ALLOWED)
                        return {'message': messages.METHOD_NOT_ALLOWED}, 405

                    try:

                        headers = dict(request.headers)
                        headers['X-TRANSACTION-ID'] = request.transaction_id
                        headers['X-ORIGIN'] = config_env('ORIGIN')

                        # Forward the request to the microservice
                        url = f'{service.service_host}/{service.service_name}/{path if path else ""}'
                        pprint.pprint(request.__dict__)

                        response = requests.request(
                            method=request.method,
                            url=url,
                            headers=headers,
                            params=request.args,
                            data=request.get_data(),
                        )

                        # Return the response from the microservice
                        response = Response(
                            response=response.content,
                            status=response.status_code,
                            headers=dict(response.headers),
                            mimetype=response.headers['Content-Type']
                        )

                        return response
                    except requests.exceptions.RequestException as e:

                        logging.send_log_kafka('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               e.args[0])
                        return {'message': messages.SERVICE_UNAVAILABLE}, 503

            # if the URL is not in the pattern of a route, return 404
            return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class SwaggerResource(Resource):
    @staticmethod
    def get():
        try:
            microservices = []
            combined_swagger = {
                "swagger": "2.0",
                "info": {
                    "description": "",
                    "version": "1.0.0",
                    "title": "API Gateway",

                },
                "basePath": "/api",
            }
            paths = {}
            definitions = {}
            security_definitions = {
                "Authorization": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header"
                }
            }

            # Get all services
            services = repository_service.get_all()

            # Validate if the service has routes
            for service in services:
                routes = repository_service_routes.get_by_service_id(service_id=service.id)
                for route in routes:
                    if 'swagger.json' in route.route:
                        microservices.append({
                            'service': service,
                            'service_host': service.service_host,
                            'route': route.route
                        })
                        break

            for microservice in microservices:
                service = microservice['service']
                service_url = f'{microservice["service_host"]}{microservice["route"]}'
                try:
                    headers = dict(request.headers)
                    headers['X-TRANSACTION-ID'] = request.transaction_id
                    headers['X-ORIGIN'] = config_env('ORIGIN')

                    response = requests.request(
                        method=request.method,
                        url=service_url,
                        headers=headers,
                    )
                    if response.status_code == 200:
                        new_documentation = {
                           "swagger": response.json()
                        }

                        documentation = repository_service_documentations.get_by_service_id(service_id=service.id)
                        if documentation:
                            documentation = repository_service_documentations.update(service_documentation=documentation,
                                                                     new_service_documentation=new_documentation)
                        else:
                            documentation = repository_service_documentations.create(service=service, new_service_documentation=new_documentation)

                        paths.update(documentation.swagger['paths'])
                        definitions.update(documentation.swagger['definitions'])
                    else:
                        documentation = repository_service_documentations.get_by_service_id(service_id=service.id)
                        if documentation:
                            paths.update(documentation.swagger['paths'])
                            definitions.update(documentation.swagger['definitions'])

                        logging.send_log_kafka('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get',
                                                  messages.SERVICE_UNAVAILABLE)

                except requests.exceptions.RequestException as e:
                    documentation = repository_service_documentations.get_by_service_id(service_id=service.id)
                    if documentation:
                        paths.update(documentation.swagger['paths'])
                        definitions.update(documentation.swagger['definitions'])

                    logging.send_log_kafka('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get',
                                           messages.SERVICE_UNAVAILABLE)

            combined_swagger.update({
                "paths": paths,
                "definitions": definitions,
                "securityDefinitions": security_definitions
            })
            return combined_swagger

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class SwaggerUIResource(Resource):
    @staticmethod
    def get():
        try:
            return make_response(render_template('swagger_ui.html'))
        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'SwaggerUIResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
