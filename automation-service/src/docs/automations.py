from src import schemas



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
        'endpoint': '/automations/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(schemas.AutomationPostSchema()),
                'response': {
                    'automation': return_model_dict(schemas.AutomationGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'automations': [return_model_dict(schemas.AutomationGetSchema())],
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
        'endpoint': '/automations/<automation_uuid>/',
        'methods': [
            {
            'PATCH': {
                'request': return_model_dict(schemas.AutomationPatchSchema()),
                'response': {
                    'automation': return_model_dict(schemas.AutomationGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'automation': return_model_dict(schemas.AutomationGetSchema())
                    }
                }
            },
            {
            'DELETE':
                {
                    'response': {
                        'message': 'message'
                    }
                }
            }
        ]
    },
    {
        'endpoint': '/automations/me/',
        'methods': [
            {
            'GET':
                {
                    'response': {
                        'automations': [return_model_dict(schemas.AutomationGetSchema())],
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
            },
        ]
    },
    {
        'endpoint': '/automations/<automation_uuid>/owners/',
        'methods': [
            {
                'POST': {
                'request': return_model_dict(schemas.OwnersPostSchema()),
                'response': {
                    'owners': return_model_dict(schemas.OwnersGetSchema())
                    }
                },
                'GET':{
                    'response': {
                        'owners': return_model_dict(schemas.OwnersGetSchema()),
                        'pagination': {
                            'total_pages': 'total_pages',
                            'current_page': 'current_page',
                            'per_page': 'per_page',
                            'total_items': 'total_items',
                            'has_next': 'has_next',
                            'has_prev': 'has_prev',
                            'total_items_this_page': 'total_items_this_page',
                            'offset': 'offset'
                        }
                    }
                },
                'DELETE':{
                    'request': return_model_dict(schemas.OwnersDeleteSchema()),
                    'response': {
                        'message': 'message'
                    }
                }
            },
        ]
    },
    {
        'endpoint': '/automations/<automation_uuid>/steps/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(schemas.AutomationStepPostSchema()),
                'response': {
                    'step': return_model_dict(schemas.AutomationStepGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'steps': [return_model_dict(schemas.AutomationStepGetSchema())],
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
        'endpoint': '/automations/steps/<step_uuid>/',
        'methods': [
            {
                'PATCH': {
                    'request': return_model_dict(schemas.AutomationStepPatchSchema()),
                    'response': {
                        'automation': return_model_dict(schemas.AutomationStepGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'automation': return_model_dict(schemas.AutomationStepGetSchema())
                        }
                    }
            },
            {
                'DELETE':
                    {
                        'response': {
                            'message': 'message'
                        }
                    }
            }
        ]
    },
    {
        'endpoint': '/automations/<automation_uuid>/items/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(schemas.AutomationItemPostSchema()),
                    'response': {
                        'item': return_model_dict(schemas.AutomationItemGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(schemas.AutomationItemGetSchema())],
                            'pagination': {
                                'total_pages': 'total_pages',
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
        'endpoint': '/automations/items/<item_uuid>/',
        'methods': [
            {
                'GET':{
                        'response': {
                            'automation': return_model_dict(schemas.AutomationItemGetSchema())
                        }
                    }

            }
        ]
    },
    {
        'endpoint': '/automations/steps/<step_uuid>/items/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(schemas.AutomationItemPostSchema()),
                    'response': {
                        'item': return_model_dict(schemas.AutomationItemGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(schemas.AutomationItemGetSchema())],
                            'pagination': {
                                'total_pages': 'total_pages',
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
        'endpoint': '/automations/items/<item_uuid>/update-status/',
        'methods': [
            {
                'PATCH': {
                    'request': return_model_dict(schemas.AutomationItemUpdateStatusPatchSchema()),
                    'response': {
                        'automation': return_model_dict(schemas.AutomationStepGetSchema())
                    }
                }
            },
        ]
    },
    {
        'endpoint': '/automations/items/<item_uuid>/history/',
        'methods': [
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(schemas.AutomationItemHistoryGetSchema())],
                            'pagination': {
                                'total_pages': 'total_pages',
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
    '/automations/': {
        'post': {
            'tags': ['automations'],
            'summary': 'Create automation',
            'description': 'Create automation',
            'parameters': [
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationPostSchema'
                    },
                    'required': True,
                    'description': 'Automation data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['automations'],
            'summary': 'Get automations',
            'description': 'Get automations',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationsGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
    },
    '/automations/{automation_uuid}/': {
        'get': {
            'tags': ['automations'],
            'summary': 'Get automation',
            'description': 'Get automation',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'patch': {
            'tags': ['automations'],
            'summary': 'Update automation',
            'description': 'Update automation',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationPatchSchema'
                    },
                    'required': True,
                    'description': 'Automation data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'delete': {
            'tags': ['automations'],
            'summary': 'Delete automation',
            'description': 'Delete automation',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/me/': {
        'get': {
            'tags': ['automations'],
            'summary': 'Get automations by user',
            'description': 'Get automations by user',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationsGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/{automation_uuid}/owners/': {
        'post': {
            'tags': ['owners'],
            'summary': 'Add owner to automation',
            'description': 'Add owner to automation',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/OwnersPostSchema'
                    },
                    'required': True,
                    'description': 'Owner data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/OwnersResponseSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['owners'],
            'summary': 'Get automation owners',
            'description': 'Get automation owners',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/OwnersGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'delete': {
            'tags': ['owners'],
            'summary': 'Delete owner from automation',
            'description': 'Delete owner from automation',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/OwnersDeleteSchema'
                    },
                    'required': True,
                    'description': 'Owner uuid'
                }
            ],
            "responses": {
              "200": {
                "description": "OK",
                "schema": {
                    "$ref": "#/definitions/OwnersResponseSchema"
                }
              }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/{automation_uuid}/steps/': {
        'post': {
            'tags': ['steps'],
            'summary': 'Create step',
            'description': 'Create step',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepPostSchema'
                    },
                    'required': True,
                    'description': 'Step data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['steps'],
            'summary': 'Get steps',
            'description': 'Get steps',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepsGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/steps/{step_uuid}/': {
        'get': {
            'tags': ['steps'],
            'summary': 'Get step',
            'description': 'Get step',
            'parameters': [
                {
                    'name': 'step_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Step uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'patch': {
            'tags': ['steps'],
            'summary': 'Update step',
            'description': 'Update step',
            'parameters': [
                {
                    'name': 'step_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Step uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepPatchSchema'
                    },
                    'required': True,
                    'description': 'Step data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationStepGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'delete': {
            'tags': ['steps'],
            'summary': 'Delete step',
            'description': 'Delete step',
            'parameters': [
                {
                    'name': 'step_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Step uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK'
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/{automation_uuid}/items/': {
        'post': {
            'tags': ['items'],
            'summary': 'Create item',
            'description': 'Create item',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemPostSchema'
                    },
                    'required': True,
                    'description': 'Item data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemPostSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['items'],
            'summary': 'Get items',
            'description': 'Get items',
            'parameters': [
                {
                    'name': 'automation_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Automation uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemsGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/items/{item_uuid}/': {
        'get': {
            'tags': ['items'],
            'summary': 'Get item',
            'description': 'Get item',
            'parameters': [
                {
                    'name': 'item_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Item uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/steps/{step_uuid}/items/': {
        'post': {
            'tags': ['items'],
            'summary': 'Create item',
            'description': 'Create item',
            'parameters': [
                {
                    'name': 'step_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Step uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemPostSchema'
                    },
                    'required': True,
                    'description': 'Item data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        },
        'get': {
            'tags': ['items'],
            'summary': 'Get items',
            'description': 'Get items',
            'parameters': [
                {
                    'name': 'step_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Step uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemsGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/items/{item_uuid}/update-status/': {
        'patch': {
            'tags': ['items'],
            'summary': 'Update item status',
            'description': 'Update item status',
            'parameters': [
                {
                    'name': 'item_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Item uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemUpdateStatusPatchSchema'
                    },
                    'required': True,
                    'description': 'Item status data (values: pending, running, finished, failed, canceled, deleted, paused)'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
    '/automations/items/{item_uuid}/history/': {
        'get': {
            'tags': ['history'],
            'summary': 'Get item history',
            'description': 'Get item history',
            'parameters': [
                {
                    'name': 'item_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Item uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/AutomationItemHistoryGetSchema'
                    }
                }
            },
            'security': [
                {
                    'Authorization': [
                        'automations'
                    ]
                }
            ]
        }
    },
}

definitions = {
    ### Automations ###
    'AutomationGetSchema': convert_to_swagger_dict(schemas.AutomationGetSchema()),
    'AutomationsGetSchema': {
        'type': 'object',
        'properties': {
            'automations': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/AutomationGetSchema'
                }
            }
        }
    },
    'AutomationPostSchema': convert_to_swagger_dict(schemas.AutomationPostSchema()),
    'AutomationPatchSchema': convert_to_swagger_dict(schemas.AutomationPatchSchema()),

    ### Owners ###
    'OwnersPostSchema': {
        'type': 'object',
        'properties': {
            'owners': {
                'type': 'array',
                'items': {
                   '$ref': '#/definitions/OwnerGetSchema'
                }
            }
        }
    },
    'OwnersGetSchema': {
        'type': 'object',
        'properties': {
            'owners': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/OwnerGetSchema'
                }
            }
        }
    },
    'OwnersDeleteSchema': {
        'type': 'object',
        'properties': {
            'owners': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/OwnerGetSchema'
                }
            }
        }
    },
    'OwnerGetSchema': convert_to_swagger_dict(schemas.OwnerGetSchema()),
    'OwnersResponseSchema': {
        'type': 'object',
        'properties': {
            'owners_success': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/OwnerGetSchema'
                }
            },
            'owners_fail': {
                'type': 'array',
                'items': {
                    'properties': {
                        'uuid': {
                            'type': 'string'
                        },
                        'message': {
                            'type': 'string'
                        }
                    }
                }
            }
        }
    },

    ### Steps ###
    'AutomationStepPostSchema': convert_to_swagger_dict(schemas.AutomationStepPostSchema()),
    'AutomationStepGetSchema': convert_to_swagger_dict(schemas.AutomationStepGetSchema()),
    'AutomationStepsGetSchema': {
        'type': 'object',
        'properties': {
            'steps': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/AutomationStepGetSchema'
                }
            }
        }
    },
    'AutomationStepPatchSchema': convert_to_swagger_dict(schemas.AutomationStepPatchSchema()),

    ### Items ###
    'AutomationItemPostSchema': convert_to_swagger_dict(schemas.AutomationItemPostSchema()),
    'AutomationItemUpdateStatusPatchSchema': convert_to_swagger_dict(schemas.AutomationItemUpdateStatusPatchSchema()),
    'AutomationItemGetSchema': convert_to_swagger_dict(schemas.AutomationItemGetSchema()),
    'AutomationItemWithoutStepsGetSchema': convert_to_swagger_dict(schemas.AutomationItemWithoutStepsGetSchema()),
    'AutomationItemsGetSchema': {
        'type': 'object',
        'properties': {
            'items': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/AutomationItemWithoutStepsGetSchema'
                }
            }
        }
    },
    'AutomationItemHistoryGetSchema': convert_to_swagger_dict(schemas.AutomationItemHistoryGetSchema()),

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