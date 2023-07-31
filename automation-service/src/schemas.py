import re
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested
from src import messages


def validate_alphanumeric(value):
    if not re.match(r'^[a-zA-Z0-9 _]+$', value):
        raise ValidationError(messages.ALPHANUMERIC_ERROR)


#### AUTOMATIONS ####
class AutomationPostSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    acronym = fields.String(required=True, validate=[validate.Length(min=1, max=5), validate_alphanumeric])
    owners = fields.List(fields.Dict(), required=False, validate=validate.Length(min=0))

    class Meta:
        ordered = True


class AutomationGetSchema(Schema):
    uuid = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    acronym = fields.String(required=True)
    #created_at = fields.DateTime(required=True)
    #updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True


#### OWNERS ####
class OwnerGetSchema(Schema):
    uuid = fields.String(required=True)

    class Meta:
        ordered = True


class OwnersPostSchema(Schema):
    owners = fields.List(Nested(OwnerGetSchema), required=False, validate=validate.Length(min=0))

    class Meta:
        ordered = True


class OwnersGetSchema(Schema):
    owners = fields.List(Nested(OwnerGetSchema), required=True)

    class Meta:
        ordered = True


class OwnersDeleteSchema(Schema):
    owners = fields.List(Nested(OwnerGetSchema), required=True, validate=validate.Length(min=1))

    class Meta:
        ordered = True


class AutomationPatchSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, validate=validate.Length(min=1, max=500))
    acronym = fields.String(required=False, validate=[validate.Length(min=1, max=5), validate_alphanumeric])
    owners = fields.List(fields.Dict(), required=False, validate=validate.Length(min=0))

    class Meta:
        ordered = True


#### STEPS ####
class AutomationStepPostSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    step = fields.Integer(required=True, validate=validate.Range(min=1))
    topic = fields.String(required=True, validate=[validate.Length(min=1, max=100), validate_alphanumeric])
    try_count = fields.Integer(required=True, validate=validate.Range(min=1))

    class Meta:
        ordered = True


class AutomationStepGetSchema(Schema):
    uuid = fields.String(required=True)
    automation_id = fields.Integer(required=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    step = fields.Integer(required=True)
    topic = fields.String(required=True)
    try_count = fields.Integer(required=True)
    #created_at = fields.DateTime(required=True)
    #updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True


class AutomationStepPatchSchema(Schema):
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(required=False, validate=validate.Length(min=1, max=500))
    step = fields.Integer(required=False, validate=validate.Range(min=1))
    topic = fields.String(required=False, validate=validate.Length(min=1, max=100))

    class Meta:
        ordered = True


class StepsResponseItemSchema(Schema):
    max_steps = fields.Integer(required=True)
    current_step = Nested(AutomationStepGetSchema, required=True)
    next_step = Nested(AutomationStepGetSchema, required=False)


#### ITEMS ####
class AutomationItemPostSchema(Schema):
    data = fields.Dict(required=True)


class AutomationItemGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)
    #created_at = fields.DateTime(required=True)
    #updated_at = fields.DateTime(required=True)
    steps = Nested(StepsResponseItemSchema, required=True)
    try_count = fields.Integer(required=False)

    class Meta:
        ordered = True


class AutomationItemWithoutStepsGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)

    class Meta:
        ordered = True


class AutomationItemUpdateStatusPatchSchema(Schema):
    STATUS_CHOICES = ['pending', 'running', 'finished', 'failed', 'canceled', 'deleted', 'paused']
    status = fields.String(required=True, validate=validate.OneOf(choices=STATUS_CHOICES))

    class Meta:
        ordered = True


class AutomationItemHistoryGetSchema(Schema):
    uuid = fields.String(required=True)
    description = fields.String(required=True)
    created_at = fields.DateTime(required=True)

    class Meta:
        ordered = True



