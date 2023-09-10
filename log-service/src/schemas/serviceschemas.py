from marshmallow import Schema, fields, validate


class ServicePostSchema(Schema):
    service_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    level = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    module_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    function_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    transaction_id = fields.Str(required=False)

    class Meta:
        ordered = True


class ServiceGetSchema(Schema):
    uuid = fields.Str(required=True)
    datetime = fields.DateTime(required=True)
    service_name = fields.Str(required=True)
    level = fields.Str(required=True)
    module_name = fields.Str(required=True)
    function_name = fields.Str(required=True)
    message = fields.Str(required=True)
    transaction_id = fields.Str(required=True)

    class Meta:
        ordered = True
