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
        'endpoint':'/auth/users/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(schemas.UserPostSchema()),
                'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
            {
            'GET':
                {
                    'response': {
                        'users': [return_model_dict(schemas.UserGetSchema())],
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
        'endpoint':'/auth/users/<user_uuid>/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(schemas.UserPostSchema()),
                'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
            {
            'GET':
                {
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
            {
            'PATCH':
                {
                    'request': return_model_dict(schemas.UserPatchSchema()),
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
            {
            'DELETE':
                {
                    'response': {'message': 'message'}
                }
            }

        ]
    },
    {
        'endpoint':'/auth/users/me/',
        'methods': [
            {
            'GET': {
                'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
            {
            'PATCH':
                {
                    'request': return_model_dict(schemas.UserPatchSchema()),
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            },
        ]
    },
    {
        'endpoint': '/auth/users/<user_uuid>/change-role/',
        'methods': [
            {
                'POST': {
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            }
        ]
    },
    {
        'endpoint':'/auth/users/me/change-password/',
        'methods': [
            {
            'POST': {
                'request': return_model_dict(schemas.UserChangePasswordSchema()),
                'response': {'message': 'message'}
                }
            }
        ]
    },
    {
        'endpoint': '/auth/validate/token/',
        'methods': [
            {
                'GET': {
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            }
        ]
    },
    {
        'endpoint': '/auth/validate/admin/',
        'methods': [
            {
                'GET': {
                    'response': {'user': return_model_dict(schemas.UserGetSchema())}
                }
            }
        ]
    },
    {
        'endpoint': '/auth/login/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(schemas.UserLoginSchema()),
                    'response': {'token': 'token'}
                }
            }
        ]

    },
    {
        'endpoint': '/auth/logout/',
        'methods': [
            {
                'GET': {
                    'response': {'message': 'message'}
                }
            }
        ]

    },
    {
        'endpoint': '/auth/send-email-validation/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(schemas.UserSendEmailValidationSchema()),
                    'response': {'message': 'message'}
                }
            }
        ]

    },
    {
        'endpoint': '/auth/validate-email/<token>',
        'methods': [
            {
                'GET': {
                    'response': {'message': 'message'}
                }
            }
        ]

    },
    {
        'endpoint': '/auth/forgot-password/',
        'methods': [
            {
                'POST': {
                    'request': return_model_dict(schemas.ForgotPasswordSchema()),
                    'response': {'message': 'message'}
                }
            }
        ]

    },
    {
        'endpoint': '/auth/reset-password/<token>/',
        'methods': [
            {
                'GET': {
                    'response': {'message': 'message'}
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

        types.update({"type": field_type})
        if field_format:
            types.update({"format": field_format})

        swagger_dict["properties"][field_name] = types
    return swagger_dict

paths = {
    '/auth/login/': {
        'post': {
            'tags': ['auth'],
            'summary': 'Login',
            'description': 'Login',
            'parameters' : [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Login',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserLoginSchema'
                    },
                    'example': {
                        'email': 'admin@admin.com',
                        'password': 'admin'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserLoginResponseSchema'
                    }
                }
            }
        }
    },
    '/auth/logout/': {
        'get': {
            'tags': ['auth'],
            'summary': 'Logout',
            'description': 'Logout',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/users/': {
        'post': {
            'tags': ['users'],
            'summary': 'Create user',
            'description': 'Create user',
            'parameters': [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Create user',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserPostSchema'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        },
        'get': {
            'tags': ['users'],
            'summary': 'Get users',
            'description': 'Get users',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UsersGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }

    },
    '/auth/users/{user_uuid}/': {
        'get': {
            'tags': ['users'],
            'summary': 'Get user',
            'description': 'Get user',
            'parameters': [
                {
                    'in': 'path',
                    'name': 'user_uuid',
                    'description': 'User uuid',
                    'required': True,
                    'type': 'string'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        },
        'patch': {
            'tags': ['users'],
            'summary': 'Update user',
            'description': 'Update user',
            'parameters': [
                {
                    'in': 'path',
                    'name': 'user_uuid',
                    'description': 'User uuid',
                    'required': True,
                    'type': 'string'
                },
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Update user',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserPatchSchema'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        },
    },
    '/auth/users/me/': {
        'get': {
            'tags': ['users'],
            'summary': 'Get current user',
            'description': 'Get current user',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        },
        'patch': {
            'tags': ['users'],
            'summary': 'Update current user',
            'description': 'Update current user',
            'parameters': [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Update current user',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserPatchSchema'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/users/{user_uuid}/change-role/': {
        'post': {
            'tags': ['users'],
            'summary': 'Change user role',
            'description': 'Change user role',
            'parameters': [
                {
                    'in': 'path',
                    'name': 'user_uuid',
                    'description': 'User uuid',
                    'required': True,
                    'type': 'string'
                },
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            'security': [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/users/me/change-password/': {
        'post': {
            'tags': ['users'],
            'summary': 'Change password',
            'description': 'Change password',
            'parameters': [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Change password',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserChangePasswordSchema'
                    }
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
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/validate/token/': {
        'get': {
            'tags': ['auth'],
            'summary': 'Validate token',
            'description': 'Validate token',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/validate/admin/': {
        'get': {
            'tags': ['auth'],
            'summary': 'Validate admin',
            'description': 'Validate admin',
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/UserGetSchema'
                    }
                }
            },
            "security": [
                {
                    "Authorization": [
                        "auth"
                    ]
                }
            ]
        }
    },
    '/auth/send-email-validation/': {
        'post': {
            'tags': ['auth'],
            'summary': 'Send email validation',
            'description': 'Send email validation',
            'parameters': [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Send email validation',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserSendEmailValidationSchema'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            }
        }
    },
    '/auth/validate-email/{token}': {
        'get': {
            'tags': ['auth'],
            'summary': 'Validate email',
            'description': 'Validate email',
            'parameters': [
                {
                    'in': 'path',
                    'name': 'token',
                    'description': 'Token',
                    'required': True,
                    'type': 'string'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            }
        }
    },
    '/auth/forgot-password/': {
        'post': {
            'tags': ['auth'],
            'summary': 'Forgot password',
            'description': 'Forgot password',
            'parameters': [
                {
                    'in': 'body',
                    'name': 'body',
                    'description': 'Forgot password',
                    'required': True,
                    'schema': {
                        '$ref': '#/definitions/UserForgotPasswordSchema'
                    }
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            }
        }
    },
    '/auth/reset-password/{token}/': {
        'get': {
            'tags': ['auth'],
            'summary': 'Reset password',
            'description': 'Reset password',
            'parameters': [
                {
                    'in': 'path',
                    'name': 'token',
                    'description': 'Token',
                    'required': True,
                    'type': 'string'
                }
            ],
            'responses': {
                '200': {
                    'description': 'OK',
                    'schema': {
                        '$ref': '#/definitions/MessageSchema'
                    }
                }
            }
        },
    }
}

definitions = {
    'UserPostSchema': convert_to_swagger_dict(schemas.UserPostSchema()),
    'UsersGetSchema': {
        'type': 'object',
        'properties': {
            'users': {
                'type': 'array',
                'items': {
                    '$ref': '#/definitions/UserGetSchema'
                }
            }
        }
    },
    'UserGetSchema': convert_to_swagger_dict(schemas.UserGetSchema()),
    'UserPatchSchema': convert_to_swagger_dict(schemas.UserPatchSchema()),
    'UserLoginSchema': convert_to_swagger_dict(schemas.UserLoginSchema()),
    'UserLoginResponseSchema': {
        'type:': 'object',
        'properties': {
            'token': {
                'type': 'string'
            },
        }
    },
    'UserChangePasswordSchema': convert_to_swagger_dict(schemas.UserChangePasswordSchema()),
    'UserForgotPasswordSchema': convert_to_swagger_dict(schemas.ForgotPasswordSchema()),
    'UserResetPasswordSchema': convert_to_swagger_dict(schemas.UserSendEmailValidationSchema()),
    'UserSendEmailValidationSchema': convert_to_swagger_dict(schemas.UserSendEmailValidationSchema()),
    'MessageSchema': {
        'type': 'object',
        'properties': {
            'message': {
                'type': 'string'
            },
        }
    },
}

doc_swagger = {
    "paths": paths,
    "definitions": definitions
}


