import re
from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.fields import Nested
from src import messages


def choices_status():
    return ['pending', 'running', 'finished', 'failed', 'canceled', 'deleted', 'paused']



#### ITEMS ####
class ItemPostSchema(Schema):
    data = fields.Dict(required=True)


class ItemGetSchema(Schema):
    uuid = fields.String(required=True)
    data = fields.Dict(required=True)
    status = fields.String(required=True)

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

    class Meta:
        ordered = True


class ItemUpdateStatusPatchSchema(Schema):
    status = fields.String(required=True, validate=validate.OneOf(choices=choices_status()))

    class Meta:
        ordered = True


class ItemHistoricGetSchema(Schema):
    uuid = fields.String(required=True)
    description = fields.String(required=True)
    created_at = fields.DateTime(required=True)

    class Meta:
        ordered = True



