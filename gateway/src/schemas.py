from marshmallow import Schema, fields, validate
from marshmallow.fields import Nested


class ServicePostSchema(Schema):
    service_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    service_host = fields.String(required=True, validate=validate.Length(min=1, max=500))


class ServiceGetSchema(Schema):
    uuid = fields.String(required=True)
    service_name = fields.String(required=True)
    service_host = fields.String(required=True)
    service_status = fields.String(required=True)
    service_routes = Nested('ServiceRouteGetSchema', many=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True


class ServiceRoutePostSchema(Schema):
    route = fields.String(required=True, validate=validate.Length(min=1, max=100))
    args = fields.String(required=True, validate=validate.Length(min=0, max=500))
    methods_allowed = fields.List(fields.String, required=True, validate=validate.Length(min=1))
    required_auth = fields.Boolean(required=False)
    required_admin = fields.Boolean(required=False)


class ServiceRouteGetSchema(Schema):
    uuid = fields.String(required=True)
    route = fields.String(required=True)
    args = fields.String(required=True)
    methods_allowed = fields.List(fields.String, required=True)
    required_auth = fields.Boolean(required=True)
    required_admin = fields.Boolean(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)

    class Meta:
        ordered = True