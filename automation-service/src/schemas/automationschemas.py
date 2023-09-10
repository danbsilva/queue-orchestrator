import re
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested
from src import messages


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9 _]+$', value):
        raise ValidationError(messages.ALPHANUMERIC_ERROR)


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
