from marshmallow import Schema, fields, validate


class ServiceLogPostSchema(Schema):
    service_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    transaction_id = fields.Str(required=False)
    level = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    module_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    function_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))


class ServiceLogGetSchema(Schema):
    uuid = fields.Str(required=True)
    datetime = fields.DateTime(required=True)
    service_name = fields.Str(required=True)
    transaction_id = fields.Str(required=True)
    level = fields.Str(required=True)
    module_name = fields.Str(required=True)
    function_name = fields.Str(required=True)
    message = fields.Str(required=True)


class RequestLogPostSchema(Schema):
    service = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    ip = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    method = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    endpoint = fields.Str(required=True, validate=[validate.Length(min=1, max=15)])
    status = fields.Int(required=True, validate=validate.Range(min=1))
    duration = fields.Float(required=True, validate=validate.Range(min=1))


class RequestLogGetSchema(Schema):
    uuid = fields.Str(required=True)
    datetime = fields.DateTime(required=True)
    service = fields.Str(required=True)
    transaction_id = fields.Str(required=True)
    ip = fields.Str(required=True)
    method = fields.Str(required=True)
    endpoint = fields.Str(required=True)
    params = fields.Str(required=False)
    status = fields.Int(required=True)
    duration = fields.Float(required=True)

