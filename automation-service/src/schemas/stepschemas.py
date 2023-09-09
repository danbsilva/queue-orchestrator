import re
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested
from src import messages


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9 _]+$', value):
        raise ValidationError(messages.ALPHANUMERIC_ERROR)


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


