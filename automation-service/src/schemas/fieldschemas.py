import re
from marshmallow import Schema, fields, validate
from src import messages
from src.schemas.stepschemas import StepGetSchema

def choices_type():
    return ['string', 'integer', 'float', 'boolean', 'date', 'datetime', 'time', 'list', 'dict', 'url', 'email']


#### DYNAMIC SCHEMA ####
class DynamicSchema(Schema):
    class Meta:
        ordered = True


### FIELDS ####
class FieldPostSchema(Schema):
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error=messages.FIELD_NAME_RANGE_ERROR)
        ]
    )
    alias = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error=messages.FIELD_ALIAS_RANGE_ERROR)
        ]
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=500, error=messages.FIELD_DESCRIPTION_RANGE_ERROR)
        ]
    )
    type = fields.String(
        required=True,
        validate=[
            validate.OneOf(
                choices=choices_type(),
                error=messages.FIELD_TYPE_ERROR
            )
        ]
    )
    required = fields.Boolean(
        required=True,
        validate=[
            validate.OneOf(choices=[True, False], error=messages.FIELD_REQUIRED_BOOLEAN_ERROR)
        ]
    )
    default = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=30, error=messages.FIELD_DESCRIPTION_RANGE_ERROR)
        ]
    )
    options = fields.List(
        fields.String(),
        required=False,
        validate=[
            validate.Length(min=1, error=messages.FIELD_OPTIONS_RANGE_ERROR)
        ]
    )

    class Meta:
        ordered = True


class FieldGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    alias = fields.String(required=True)
    description = fields.String(required=True)
    type = fields.String(required=True)
    required = fields.Boolean(required=True)
    default = fields.String(required=False)
    options = fields.List(fields.String(), required=False)
    step = fields.Nested(StepGetSchema, required=True)

    class Meta:
        ordered = True


class FieldPatchSchema(Schema):
    name = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=100, error=messages.FIELD_NAME_RANGE_ERROR)
        ]
    )
    alias = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=100, error=messages.FIELD_ALIAS_RANGE_ERROR)
        ]
    )
    description = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=500, error=messages.FIELD_DESCRIPTION_RANGE_ERROR)
        ]
    )
    type = fields.String(
        required=False,
        validate=[
            validate.OneOf(
                choices=choices_type(),
                error=messages.FIELD_TYPE_ERROR
            )
        ]
    )
    required = fields.Boolean(
        required=False,
        validate=[
            validate.OneOf(choices=[True, False], error=messages.FIELD_REQUIRED_BOOLEAN_ERROR)
        ]
    )
    default = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=500, error=messages.FIELD_DESCRIPTION_RANGE_ERROR)
        ]
    )
    options = fields.List(
        fields.String(),
        required=False,
        validate=[
            validate.Length(min=1, error=messages.FIELD_OPTIONS_RANGE_ERROR)
        ]
    )

    class Meta:
        ordered = True

