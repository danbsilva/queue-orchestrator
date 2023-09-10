import re
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested
from src import messages


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9 _]+$', value):
        raise ValidationError(messages.ALPHANUMERIC_ERROR)


def choices_type():
    return ['string', 'integer', 'float', 'boolean', 'date', 'datetime', 'time', 'list', 'dict', 'url', 'email']


#### DYNAMIC SCHEMA ####
class DynamicSchema(Schema):
    class Meta:
        ordered = True


#### AUTOMATIONS ####
class AutomationPostSchema(Schema):
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error=messages.AUTOMATION_NAME_RANGE_ERROR)
        ]
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=500, error=messages.AUTOMATION_DESCRIPTION_RANGE_ERROR)
        ]
    )
    acronym = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=3, error=messages.AUTOMATION_ACRONYM_RANGE_ERROR),
            validate_alphanumeric
        ]
    )

    class Meta:
        ordered = True


class AutomationGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    acronym = fields.String(required=True)

    class Meta:
        ordered = True


class AutomationPatchSchema(Schema):
    name = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=100, error=messages.AUTOMATION_NAME_RANGE_ERROR)
        ]
    )
    description = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=500, error=messages.AUTOMATION_DESCRIPTION_RANGE_ERROR)
        ]
    )
    acronym = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=5, error=messages.AUTOMATION_ACRONYM_RANGE_ERROR),
            validate_alphanumeric
        ]
    )

    class Meta:
        ordered = True


#### OWNERS ####
class OwnerPostSchema(Schema):
    uuid = fields.String(
        required=True
    )

    class Meta:
        ordered = True


    class Meta:
        ordered = True


class OwnerGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    email = fields.String(required=True)

    class Meta:
        ordered = True


class OwnersGetSchema(Schema):
    owners = fields.List(
        Nested(OwnerGetSchema),
        required=True
    )

    class Meta:
        ordered = True


class OwnerDeleteSchema(Schema):
    uuid = fields.String(
        required=True
    )

    class Meta:
        ordered = True



#### STEPS ####
class StepPostSchema(Schema):
    name = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error=messages.STEP_NAME_RANGE_ERROR)
        ]
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=500, error=messages.STEP_DESCRIPTION_RANGE_ERROR)
        ]
    )
    step = fields.Integer(
        required=True,
        validate=[
            validate.Range(min=1, max=100, error=messages.STEP_RANGE_ERROR)
        ]
    )
    topic = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error=messages.STEP_TOPIC_RANGE_ERROR),
            validate_alphanumeric
        ]
    )
    try_count = fields.Integer(
        required=True,
        validate=[
            validate.Range(min=1, max=5, error=messages.STEP_TRY_COUNT_RANGE_ERROR)
        ]
    )

    class Meta:
        ordered = True


class StepGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    step = fields.Integer(required=True)
    topic = fields.String(required=True)
    try_count = fields.Integer(required=True)
    automation = Nested(AutomationGetSchema, required=True)

    class Meta:
        ordered = True


class StepPatchSchema(Schema):
    name = fields.String(
        required=False,
        validate=validate.Length(min=1, max=100, error=messages.STEP_NAME_RANGE_ERROR)
    )
    description = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=500, error=messages.STEP_DESCRIPTION_RANGE_ERROR)
        ]
    )
    step = fields.Integer(
        required=False,
        validate=[
            validate.Range(min=1, max=100, error=messages.STEP_RANGE_ERROR)
        ]
    )
    topic = fields.String(
        required=False,
        validate=[
            validate.Length(min=1, max=100, error=messages.STEP_TOPIC_RANGE_ERROR),
            validate_alphanumeric
        ]
    )
    try_count = fields.Integer(
        required=False,
        validate=[
            validate.Range(min=1, max=5, error=messages.STEP_TRY_COUNT_RANGE_ERROR)
        ]
    )

    class Meta:
        ordered = True


class StepsResponseItemSchema(Schema):
    max_steps = fields.Integer(required=True)
    current_step = Nested(StepGetSchema, required=True)
    next_step = Nested(StepGetSchema, required=False)

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
    step = Nested(StepGetSchema, required=True)
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


#### ITEMS ####
class ItemPostSchema(Schema):
    data = fields.Dict(required=True)


class ItemGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)
    step = Nested(StepGetSchema, required=True)

    class Meta:
        ordered = True


class ItemPatchSchema(Schema):
    data = fields.Dict(required=True)

    class Meta:
        ordered = True


class ItemWithoutStepsGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)
    step = Nested(StepGetSchema, required=True)

    class Meta:
        ordered = True


class ItemUpdateStatusPatchSchema(Schema):
    STATUS_CHOICES = ['pending', 'running', 'finished', 'failed', 'canceled', 'deleted', 'paused']
    status = fields.String(required=True, validate=validate.OneOf(choices=STATUS_CHOICES))

    class Meta:
        ordered = True


class ItemHistoricGetSchema(Schema):
    uuid = fields.String(required=True)
    description = fields.String(required=True)
    created_at = fields.DateTime(required=True)

    class Meta:
        ordered = True



