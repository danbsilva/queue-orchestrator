import re
from decouple import config as config_env
from src import logging

import requests
from flask import Response, request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.extensions.flask_cache import cache

from src import schemas, kafka
from src import repository_service, repository_service_routes
from src import messages
from src.providers import token_provider

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
                pattern_uuid = r'[a-f0-9-]+'  # pattern to validate UUID
                pattern_jwt = r'[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]+'  # pattern to validate JWT

                if args:  # if the route has arguments, the URL must be in the pattern
                    pattern = endpoint.replace(args, f'({pattern_uuid}|{pattern_jwt})')
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
                    if request.method not in route.methods_allowed:
                        logging.send_log_kafka('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               messages.METHOD_NOT_ALLOWED)
                        return {'message': messages.METHOD_NOT_ALLOWED}, 405

                    try:

                        headers = dict(request.headers)
                        headers['X-TRANSACTION-ID'] = request.transaction_id
                        headers['X-ORIGIN'] = config_env('ORIGIN')

                        # Forward the request to the microservice
                        url = f'{service.service_host}/{service.service_name}/{path if path else ""}'

                        response = requests.request(
                            method=request.method,
                            url=url,
                            headers=headers,
                            params=request.args,
                            data=request.get_data(),
                        )

                        # Return the response from the microservice
                        return Response(
                            response=response.content,
                            status=response.status_code,
                            headers=dict(response.headers),
                        )
                    except requests.exceptions.RequestException as e:

                        logging.send_log_kafka('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               e.args[0])
                        return {'message': messages.SERVICE_UNAVAILABLE}, 503

            # if the URL is not in the pattern of a route, return 404
            return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
