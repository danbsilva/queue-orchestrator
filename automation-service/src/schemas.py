import re
from marshmallow import Schema, fields, validate, ValidationError

from src import messages


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9 _]+$', value):
        raise ValidationError(messages.ALPHANUMERIC_ERROR)


class AutomationPostSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    acronym = fields.String(required=True, validate=[validate.Length(min=1, max=5), validate_alphanumeric])
    owners = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1))


class AutomationGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    acronym = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True


class OwnersGetSchema(Schema):
    owners = fields.List(fields.Dict(), required=True)


class AutomationPatchSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, validate=validate.Length(min=1, max=500))
    acronym = fields.String(required=False, validate=[validate.Length(min=1, max=5), validate_alphanumeric])
    owners = fields.List(fields.Dict(), required=False, validate=validate.Length(min=1))

        
class AutomationStepPostSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    step = fields.Integer(required=True, validate=validate.Range(min=1))
    topic = fields.String(required=True, validate=[validate.Length(min=1, max=100), validate_alphanumeric])
    try_count = fields.Integer(required=True, validate=validate.Range(min=1))
    

class AutomationStepGetSchema(Schema):
    uuid = fields.String(required=True)
    automation_id = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    step = fields.Integer(required=True)
    topic = fields.String(required=True)
    try_count = fields.Integer(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True


class AutomationStepPatchSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, validate=validate.Length(min=1, max=500))
    step = fields.Integer(required=False, validate=validate.Range(min=1))
    topic = fields.String(required=False, validate=validate.Length(min=1, max=100))


class AutomationItemPostSchema(Schema):
    data = fields.Dict(required=True)
    status = fields.String(required=False)


class AutomationItemGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    #history = fields.Nested('AutomationItemHistoryGetSchema', many=True)

    class Meta:
        ordered = True


class AutomationStepItemGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)
    automation_step = fields.Nested('AutomationStepGetSchema', many=False)

    class Meta:
        ordered = True


class AutomationItemPatchSchema(Schema):
    data = fields.Dict(required=True)
    status = fields.String(required=False)
    steps = fields.Dict(required=True)


class AutomationItemHistoryGetSchema(Schema):
    uuid = fields.String(required=True)
    description = fields.String(required=True)
    created_at = fields.DateTime(required=True)

    class Meta:
        ordered = True



