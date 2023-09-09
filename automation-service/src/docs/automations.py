from src.schemas import automationschemas, stepschemas, fieldschemas, itemschemas


def return_model_dict(schema):
    schema_attributes = schema.fields
    model_dict = {}

    # Iterar sobre os atributos para obter os nomes dos campos
    for field_name, field_obj in schema_attributes.items():
        model_dict[field_name] = field_obj.__class__.__name__  #

    return model_dict


docs_endpoints = [
    # Health
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

    # Automations
    {
        'endpoint': '/automations/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(automationschemas.AutomationPostSchema()),
                'response': {
                    'automation': return_model_dict(automationschemas.AutomationGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'automations': [return_model_dict(automationschemas.AutomationGetSchema())],
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
                'request': return_model_dict(automationschemas.AutomationPatchSchema()),
                'response': {
                    'automation': return_model_dict(automationschemas.AutomationGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'automation': return_model_dict(automationschemas.AutomationGetSchema())
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
                        'automations': [return_model_dict(automationschemas.AutomationGetSchema())],
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

    # Owners
    {
        'endpoint': '/automations/<automation_uuid>/owners/',
        'methods': [
            {
                'POST': {
                'request': return_model_dict(automationschemas.OwnerPostSchema()),
                'response': {
                    'owners': return_model_dict(automationschemas.OwnersGetSchema())
                    }
                },
                'GET':{
                    'response': {
                        'owners': return_model_dict(automationschemas.OwnersGetSchema()),
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
                    'request': return_model_dict(automationschemas.OwnerDeleteSchema()),
                    'response': {
                        'message': 'message'
                    }
                }
            },
        ]
    },

    # Steps
    {
        'endpoint': '/automations/<automation_uuid>/steps/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(stepschemas.StepPostSchema()),
                'response': {
                    'step': return_model_dict(stepschemas.StepGetSchema())
                    }
                }
            },
            {
            'GET':
                {
                    'response': {
                        'steps': [return_model_dict(stepschemas.StepGetSchema())],
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
                    'request': return_model_dict(stepschemas.StepPatchSchema()),
                    'response': {
                        'automation': return_model_dict(stepschemas.StepGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'automation': return_model_dict(stepschemas.StepGetSchema())
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

    # Fields
    {
        'endpoint': '/automations/steps/<step_uuid>/fields/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(fieldschemas.FieldPostSchema()),
                    'response': {
                        'field': return_model_dict(fieldschemas.FieldGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'fields': [return_model_dict(fieldschemas.FieldGetSchema())],
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
        'endpoint': '/automations/steps/fields/<field_uuid>/',
        'methods': [
            {
                'GET':
                    {
                        'response': {
                            'field': return_model_dict(fieldschemas.FieldGetSchema())
                        }
                    }
            },
            {
                'PATCH': {
                    'request': return_model_dict(fieldschemas.FieldPatchSchema()),
                    'response': {
                        'field': return_model_dict(fieldschemas.FieldGetSchema())
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

    # Items
    {
        'endpoint': '/automations/<automation_uuid>/items/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(itemschemas.ItemPostSchema()),
                    'response': {
                        'item': return_model_dict(itemschemas.ItemGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(itemschemas.ItemGetSchema())],
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
                            'automation': return_model_dict(itemschemas.ItemGetSchema())
                        }
                    }
            },
            {
                'PATCH': {
                    'request': return_model_dict(itemschemas.ItemPatchSchema()),
                    'response': {
                        'automation': return_model_dict(itemschemas.ItemGetSchema())
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
        'endpoint': '/automations/steps/<step_uuid>/items/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(itemschemas.ItemPostSchema()),
                    'response': {
                        'item': return_model_dict(itemschemas.ItemGetSchema())
                    }
                }
            },
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(itemschemas.ItemGetSchema())],
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
                    'request': return_model_dict(itemschemas.ItemUpdateStatusPatchSchema()),
                    'response': {
                        'automation': return_model_dict(stepschemas.StepGetSchema())
                    }
                }
            },
        ]
    },

    # Item Historic
    {
        'endpoint': '/automations/items/<item_uuid>/historic/',
        'methods': [
            {
                'GET':
                    {
                        'response': {
                            'items': [return_model_dict(itemschemas.ItemHistoricGetSchema())],
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

    # Automations
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

    # Owners
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
                        '$ref': '#/definitions/OwnerPostSchema'
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
                        '$ref': '#/definitions/OwnerDeleteSchema'
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

    # Steps
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
                        '$ref': '#/definitions/StepPostSchema'
                    },
                    'required': True,
                    'description': 'Step data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/StepGetSchema'
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
                        '$ref': '#/definitions/StepsGetSchema'
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
                        '$ref': '#/definitions/StepGetSchema'
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
                        '$ref': '#/definitions/StepPatchSchema'
                    },
                    'required': True,
                    'description': 'Step data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/StepGetSchema'
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

    # Fields
    '/automations/steps/{step_uuid}/fields/': {
        'post': {
            'tags': ['fields'],
            'summary': 'Create field',
            'description': 'Create field',
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
                        '$ref': '#/definitions/FieldPostSchema'
                    },
                    'required': True,
                    'description': 'Field data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/FieldGetSchema'
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

            'tags': ['fields'],
            'summary': 'Get fields',
            'description': 'Get fields',
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
                        '$ref': '#/definitions/FieldsGetSchema'
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
    '/automations/steps/fields/{field_uuid}/': {
        'get': {
            'tags': ['fields'],
            'summary': 'Get field',
            'description': 'Get field',
            'parameters': [
                {
                    'name': 'field_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Field uuid'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/FieldGetSchema'
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
            'tags': ['fields'],
            'summary': 'Update field',
            'description': 'Update field',
            'parameters': [
                {
                    'name': 'field_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Field uuid'
                },
                {
                    'name': 'body',
                    'in': 'body',
                    'schema': {
                        '$ref': '#/definitions/FieldPatchSchema'
                    },
                    'required': True,
                    'description': 'Field data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/FieldGetSchema'
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
            'tags': ['fields'],
            'summary': 'Delete field',
            'description': 'Delete field',
            'parameters': [
                {
                    'name': 'field_uuid',
                    'in': 'path',
                    'type': 'string',
                    'required': True,
                    'description': 'Field uuid'
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

    # Items
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
                        '$ref': '#/definitions/ItemPostSchema'
                    },
                    'required': True,
                    'description': 'Item data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/ItemGetSchema'
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
                        '$ref': '#/definitions/ItemsGetSchema'
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
                        '$ref': '#/definitions/ItemGetSchema'
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
            'tags': ['items'],
            'summary': 'Update item',
            'description': 'Update item',
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
                        '$ref': '#/definitions/ItemPatchSchema'
                    },
                    'required': True,
                    'description': 'Item data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/ItemGetSchema'
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
            'tags': ['items'],
            'summary': 'Delete item',
            'description': 'Delete item',
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
                        '$ref': '#/definitions/ItemPostSchema'
                    },
                    'required': True,
                    'description': 'Item data'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/ItemGetSchema'
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
                        '$ref': '#/definitions/ItemsGetSchema'
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
                        '$ref': '#/definitions/ItemUpdateStatusPatchSchema'
                    },
                    'required': True,
                    'description': 'Item status data (values: pending, running, finished, failed, canceled, deleted, paused)'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/ItemGetSchema'
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

    # Item historic
    '/automations/items/{item_uuid}/historic/': {
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
                        '$ref': '#/definitions/ItemHistoricGetSchema'
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
    'AutomationGetSchema': convert_to_swagger_dict(automationschemas.AutomationGetSchema()),
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
    'AutomationPostSchema': convert_to_swagger_dict(automationschemas.AutomationPostSchema()),
    'AutomationPatchSchema': convert_to_swagger_dict(automationschemas.AutomationPatchSchema()),

    ### Owners ###
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
    'OwnerDeleteSchema': convert_to_swagger_dict(automationschemas.OwnerDeleteSchema()),
    'OwnerGetSchema': convert_to_swagger_dict(automationschemas.OwnerGetSchema()),
    'OwnerPostSchema': convert_to_swagger_dict(automationschemas.OwnerPostSchema()),
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
    'StepPostSchema': convert_to_swagger_dict(stepschemas.StepPostSchema()),
    'StepGetSchema': convert_to_swagger_dict(stepschemas.StepGetSchema()),
    'StepsGetSchema': {
        'type': 'object',
        'properties': {
            'steps': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/StepGetSchema'
                }
            }
        }
    },
    'StepPatchSchema': convert_to_swagger_dict(stepschemas.StepPatchSchema()),

    ### Fields ###
    'FieldPostSchema': convert_to_swagger_dict(fieldschemas.FieldPostSchema()),
    'FieldGetSchema': convert_to_swagger_dict(fieldschemas.FieldGetSchema()),
    'FieldsGetSchema': {
        'type': 'object',
        'properties': {
            'fields': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/FieldGetSchema'
                }
            }
        }
    },
    'FieldPatchSchema': convert_to_swagger_dict(fieldschemas.FieldPatchSchema()),

    ### Items ###
    'ItemPostSchema': convert_to_swagger_dict(itemschemas.ItemPostSchema()),
    'ItemUpdateStatusPatchSchema': convert_to_swagger_dict(itemschemas.ItemUpdateStatusPatchSchema()),
    'ItemGetSchema': convert_to_swagger_dict(itemschemas.ItemGetSchema()),
    'ItemWithoutStepsGetSchema': convert_to_swagger_dict(itemschemas.ItemWithoutStepsGetSchema()),
    'ItemsGetSchema': {
        'type': 'object',
        'properties': {
            'items': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/ItemGetSchema'
                }
            }
        }
    },
    'ItemPatchSchema': convert_to_swagger_dict(itemschemas.ItemPatchSchema()),
    'ItemHistoricGetSchema': convert_to_swagger_dict(itemschemas.ItemHistoricGetSchema()),

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