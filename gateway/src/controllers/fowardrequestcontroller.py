import re
import os
from src.logging import Logger

import requests
from flask import Response, request
from flask_restful import Resource
from marshmallow import ValidationError

from src.models.servicemodel import ServiceModel
from src.models.routemodel import RouteModel
from src import messages
from src.providers import token_provider


__module_name__ = 'src.controllers.fowardrequestcontroller'


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



# Resource to forward requests to microservices
class ForwardRequestResource(Resource):
    @staticmethod
    def dispatch_request(service_name, path=None, **kwargs):
        try:
            # Verify if the service is registered
            service = ServiceModel.get_by_service_name(service_name=service_name)

            # if the service is not registered, return 404
            if not service:
                Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                       messages.SERVICE_NAME_NOT_FOUND)
                return {'message': messages.SERVICE_NAME_NOT_FOUND}, 404

            if not service.service_status:
                Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                       messages.SERVICE_UNAVAILABLE.format(service_name))
                return {'message': messages.SERVICE_UNAVAILABLE.format(service_name)}, 503

            # Verify if the service is active
            routes = RouteModel.get_by_service_id(service_id=service.id)

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
                            Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                    token_validation[0]['message'])
                            return token_validation[0], token_validation[1]

                    # verify if the route requires admin
                    if route.required_admin:
                        admin_validation = token_provider.admin_required()  # validate if the user is admin
                        if admin_validation[1] >= 400:  # if the user is not admin, return 401
                            Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                    admin_validation[0]['message'])
                            return admin_validation[0], admin_validation[1]

                    # Verify if the method is allowed
                    for method in route.methods_allowed:
                        if request.method in method:
                            break
                    else:
                        Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               messages.METHOD_NOT_ALLOWED)
                        return {'message': messages.METHOD_NOT_ALLOWED}, 405

                    try:

                        headers = dict(request.headers)
                        headers['X-TRANSACTION-ID'] = request.transaction_id
                        headers['X-ORIGIN'] = os.getenv('ORIGIN')

                        # Forward the request to the microservice
                        url = f'{service.service_host}/{service.service_name}/{path if path else ""}'

                        Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                  messages.FORWARDING_REQUEST.format(request.method, service_name, url))

                        response = requests.request(
                            method=request.method,
                            url=url,
                            headers=headers,
                            params=request.args,
                            data=request.get_data(),
                        )

                        Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                                    messages.REQUEST_FORWARDED_SUCCESSFULLY.format(request.method, service_name, url))

                         # Return the response from the microservice
                        response = Response(
                            response=response.content,
                            status=response.status_code,
                            headers=dict(response.headers),
                            mimetype=response.headers['Content-Type']
                        )

                        Logger().dispatch('INFO', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               messages.RESPONSE_RECEIVED.format(service_name, url, response.status_code))
                        return response
                    except requests.exceptions.RequestException as e:

                        Logger().dispatch('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request',
                                               messages.SERVICE_UNAVAILABLE.format(service_name))
                        return {'message': messages.SERVICE_UNAVAILABLE.format(service_name)}, 503

            # if the URL is not in the pattern of a route, return 404
            return {'message': messages.SERVICE_ROUTE_NOT_FOUND}, 404

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'ForwardRequestResource.dispatch_request', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

