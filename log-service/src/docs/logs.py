from src.schemas import serviceschemas, requestschemas



def return_model_dict(schema):
    schema_attributes = schema.fields
    model_dict = {}

    # Iterar sobre os atributos para obter os nomes dos campos
    for field_name, field_obj in schema_attributes.items():
        model_dict[field_name] = field_obj.__class__.__name__  #

    return model_dict


docs_endpoints = [
    {
        'endpoint': '/health/',
        'methods': [
            {
                'GET': {
                    'response': 'OK'
                }
            }
        ]
    },
    {
        'endpoint': '/logs/services/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(serviceschemas.ServicePostSchema()),
                'response': {
                    'log': return_model_dict(serviceschemas.ServiceGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'logs': [return_model_dict(serviceschemas.ServiceGetSchema())],
                        'pagination': {
                            'total_pages':'total_pages',
                            'current_page': 'current_page',
                            'per_page': 'per_page',
                            'total_items': 'total_items',
                            'has_next': 'has_next',
                            'has_prev': 'has_prev',
                            'total_items_this_page': 'total_items_this_page',
                            'offset': 'offset'
                        }
                    }
                }
            }
        ]
    },
    {
        'endpoint': '/logs/requests/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(requestschemas.RequestPostSchema()),
                'response': {
                    'log': return_model_dict(requestschemas.RequestGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'logs': [return_model_dict(requestschemas.RequestGetSchema())],
                        'pagination': {
                            'total_pages':'total_pages',
                            'current_page': 'current_page',
                            'per_page': 'per_page',
                            'total_items': 'total_items',
                            'has_next': 'has_next',
                            'has_prev': 'has_prev',
                            'total_items_this_page': 'total_items_this_page',
                            'offset': 'offset'
                        }
                    }
                }
            }
        ]
    },
]


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

        print(field_name, field_type, field_format)

        types.update({"type": field_type})
        if field_format:
            types.update({"format": field_format})

        swagger_dict["properties"][field_name] = types
    return swagger_dict


paths = {
    '/logs/services/': {
        'post': {
            'tags': ['logs'],
            'summary': 'Create service log',
            'description': 'Create service log',
            'parameters': [
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/ServiceLogPostSchema'
                    }
                }
            ],
            'responses': {
                '201': {
                    'description': 'Created',
                    'schema': {
                        '$ref': '#/definitions/ServiceLogGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'logs'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['logs'],
            'summary': 'Get service logs',
            'description': 'Get service logs',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/ServiceLogGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'logs'
                    ]
                }
            ]
        }
    },
    '/logs/requests/': {
        'post': {
            'tags': ['logs'],
            'summary': 'Create request log',
            'description': 'Create request log',
            'parameters': [
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/RequestLogPostSchema'
                    }
                }
            ],
            'responses': {
                '201': {
                    'description': 'Created',
                    'schema': {
                        '$ref': '#/definitions/RequestLogGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'logs'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['logs'],
            'summary': 'Get request logs',
            'description': 'Get request logs',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/RequestLogGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'logs'
                    ]
                }
            ]
        }
    },
}

definitions = {
    'ServiceLogPostSchema': convert_to_swagger_dict(serviceschemas.ServicePostSchema()),
    'ServiceLogGetSchema': convert_to_swagger_dict(serviceschemas.ServiceGetSchema()),
    'RequestLogPostSchema': convert_to_swagger_dict(requestschemas.RequestPostSchema()),
    'RequestLogGetSchema': convert_to_swagger_dict(requestschemas.RequestGetSchema()),
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
