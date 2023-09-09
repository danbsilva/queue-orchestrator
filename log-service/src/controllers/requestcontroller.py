import os

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.models.requestmodel import RequestModel
from src.schemas import requestschemas

from src.providers import cors_provider


__module_name__ = 'src.controllers.RequestsController'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(os.getenv('PER_PAGE')), type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset


# Function to validate schema
def validate_schema(schema, data):
    try:
        schema.load(data)
    except ValidationError as e:
        return e.messages

class RequestsResource(Resource):

    @staticmethod
    @cors_provider.origins_allowed
    def get():
        page, per_page, offset = get_page_args()

        logs = RequestModel.get_all()

        pagination_logs = logs[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=len(logs))

        schema_log = requestschemas.RequestLogSchema(many=True)
        schema_data = schema_log.dump(pagination_logs)

        return {'logs': schema_data,
                'pagination': {
                    'total_pages': pagination.total_pages,
                    'current_page': page,
                    'per_page': pagination.per_page,
                    'total_items': pagination.total,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev,
                    'total_items_this_page': len(pagination_logs),
                    'offset': offset
                }}, 200
