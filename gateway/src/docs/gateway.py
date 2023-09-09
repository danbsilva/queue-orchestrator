from src import schemas


def convert_to_swagger_dict(schema):
    swagger_dict = {
        "type": "object",
        "properties": {}
    }

    for field_name, field_obj in schema.fields.items():
        field_type = field_obj.__class__.__name__.lower()
        field_format = None

        types = {}
        field_items = {}

        if field_type == "datetime":
            field_type = "string"
            field_format = "date-time"

        elif field_type == "email":
            field_type = "string"
            field_format = "email"

        elif field_type == "dict":
            field_type = "object"

        elif field_type == "list":
            field_type = "array"
            field_items.update({})
            types.update({"items": field_items})

        elif field_type == "nested":
            field_type = "object"
            field_items.update(convert_to_swagger_dict(field_obj.schema))
            types.update(field_items)

        types.update({"type": field_type})
        if field_format:
            types.update({"format": field_format})

        swagger_dict["properties"][field_name] = types
    return swagger_dict


paths = {
    '/services/': {
        'post': {
            'tags': ['services'],
            'description': 'Create a new service',
            'parameters': [
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/ServicePostSchema'},
                    'required': True
                }
            ],
            'responses': {
                '201': {
                    'description': 'Service created',
                    'schema': {'$ref': '#/definitions/ServiceGetSchema'}
                },
            }
        },
        'get': {
            'tags': ['services'],
            'description': 'Get all services',
            'responses': {
                '200': {
                    'description': 'All services',
                    'schema': {'$ref': '#/definitions/ServiceGetSchema'}
                }
            }
        }
    },
    '/services/{service_uuid}/': {
        'get': {
            'tags': ['services'],
            'description': 'Get a service',
            'parameters': [
                {
                    'name': 'service_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                }
            ],
            'responses': {
                '200': {
                    'description': 'Service',
                    'schema': {'$ref': '#/definitions/ServiceGetSchema'}
                }
            }
        },
        'patch': {
            'tags': ['services'],
            'description': 'Update a service',
            'parameters': [
                {
                    'name': 'service_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/ServicePatchSchema'},
                    'required': True
                }
            ],
            'responses': {
                '200': {
                    'description': 'Service updated',
                    'schema': {'$ref': '#/definitions/ServiceGetSchema'}
                }
            }
        }
    },
    '/services/{service_uuid}/routes/': {
        'post': {
            'tags': ['routes'],
            'description': 'Create a new route',
            'parameters': [
                {
                    'name': 'service_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/ServiceRoutePostSchema'},
                    'required': True
                }
            ],
            'responses': {
                '201': {
                    'description': 'Route created',
                    'schema': {'$ref': '#/definitions/ServiceRouteGetSchema'}
                },
            }
        },
        'get': {
            'tags': ['routes'],
            'description': 'Get all routes',
            'parameters': [
                {
                    'name': 'service_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                }
            ],
            'responses': {
                '200': {
                    'description': 'All routes',
                    'schema': {'$ref': '#/definitions/ServiceRouteGetSchema'}
                }
            }
        }
    },
    '/services/routes/{route_uuid}/': {
        'get': {
            'tags': ['routes'],
            'description': 'Get a route',
            'parameters': [
                {
                    'name': 'route_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                }
            ],
            'responses': {
                '200': {
                    'description': 'Route',
                    'schema': {'$ref': '#/definitions/ServiceRouteGetSchema'}
                }
            }
        },
        'patch': {
            'tags': ['routes'],
            'description': 'Update a route',
            'parameters': [
                {
                    'name': 'route_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/ServiceRoutePatchSchema'},
                    'required': True
                }
            ],
            'responses': {
                '200': {
                    'description': 'Route updated',
                    'schema': {'$ref': '#/definitions/ServiceRouteGetSchema'}
                }
            }
        }
    }
}

definitions = {
    
    ### Services ###
    'ServicePostSchema': convert_to_swagger_dict(schemas.ServicePostSchema()),
    'ServiceGetSchema': convert_to_swagger_dict(schemas.ServiceGetSchema()),
    'ServicePatchSchema': convert_to_swagger_dict(schemas.ServicePatchSchema()),
    'ServiceRoutePostSchema': convert_to_swagger_dict(schemas.ServiceRoutePostSchema()),
    'ServiceRouteGetSchema': convert_to_swagger_dict(schemas.ServiceRouteGetSchema()),
    'ServiceRoutePatchSchema': convert_to_swagger_dict(schemas.ServiceRoutePatchSchema()),


    ### Messages ###
    'MessageSchema': {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string'
            }
        }
    }

}

doc_swagger = {
    "paths": paths,
    "definitions": definitions
}