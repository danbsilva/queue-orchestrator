import os
from src.logging import Logger

import requests
from flask import request, make_response, render_template
from flask_restful import Resource
from marshmallow import ValidationError

from src.models.servicemodel import ServiceModel
from src.models.documentationmodel import DocumentationModel
from src.models.routemodel import RouteModel
from src import messages
from src.docs import gateway


__module_name__ = 'src.controllers.swaggercontroller'


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
            paths.update(gateway.doc_swagger['paths'])

            definitions = {}
            definitions.update(gateway.doc_swagger['definitions'])

            security_definitions = {
                "Authorization": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header"
                }
            }

            # Get all services
            services = ServiceModel.get_all()

            # Validate if the service has routes
            for service in services:
                routes = RouteModel.get_by_service_id(service_id=service.id)
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
                    headers['X-ORIGIN'] = os.getenv('ORIGIN')

                    response = requests.request(
                        method=request.method,
                        url=service_url,
                        headers=headers,
                    )
                    if response.status_code == 200:
                        new_documentation = {
                           "swagger": response.json()
                        }

                        documentation = DocumentationModel.get_by_service_id(service_id=service.id)
                        if documentation:
                            documentation = DocumentationModel.update(documentation=documentation,
                                                                     new_documentation=new_documentation)
                        else:
                            documentation = DocumentationModel.create(service=service, new_documentation=new_documentation)

                        paths.update(documentation.swagger['paths'])
                        definitions.update(documentation.swagger['definitions'])
                    else:
                        documentation = DocumentationModel.get_by_service_id(service_id=service.id)
                        if documentation:
                            paths.update(documentation.swagger['paths'])
                            definitions.update(documentation.swagger['definitions'])

                        Logger().dispatch('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get',
                                                  messages.SERVICE_UNAVAILABLE.format(service.service_name))

                except requests.exceptions.RequestException as e:
                    documentation = DocumentationModel.get_by_service_id(service_id=service.id)
                    if documentation:
                        paths.update(documentation.swagger['paths'])
                        definitions.update(documentation.swagger['definitions'])

                    Logger().dispatch('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get',
                                           messages.SERVICE_UNAVAILABLE.format(service.service_name))

            combined_swagger.update({
                "paths": paths,
                "definitions": definitions,
                "securityDefinitions": security_definitions
            })
            return combined_swagger

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'SwaggersJsonServiceResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class SwaggerUIResource(Resource):
    @staticmethod
    def get():
        try:
            return make_response(render_template('swaggerui.html'))
        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'SwaggerUIResource.get', e.args[0])
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500
