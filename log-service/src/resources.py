from decouple import config as config_env

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from marshmallow import ValidationError

from src.extensions.flask_cache import cache

from src import schemas, messages, logging
from src import repository_service_log, repository_request_log
from src.providers import token_provider


__module_name__ = 'src.resources'


# Function to get page args
def get_page_args():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', int(config_env('PER_PAGE')), type=int)
    offset = (page - 1) * per_page
    return page, per_page, offset


# Function to validate schema
def validate_schema(schema, data):
    try:
        schema.load(data)
    except ValidationError as e:
        return e.messages


class LogsServicesResource(Resource):

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def post(user_authenticated):
        try:
            data = request.get_json()
            schema_validate = validate_schema(schemas.ServiceLogPostSchema(), data)
            if schema_validate:
                logging.send_log_kafka('INFO', __module_name__, 'post', f'Error to create log: {schema_validate}')
                return {'message': schema_validate}, 400

            # add transaction id to log
            data['transaction_id'] = request.headers.get('X-TRANSACTION-ID')
            log = repository_service_log.create(data)

            schema_log = schemas.ServiceLogGetSchema()
            schema_data = schema_log.dump(log)

            return {'log': schema_data}, 201
        except Exception as e:
            logging.send_log_kafka('CRITICAL', __module_name__, 'post', f'Error to create log: {e}')
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    @cache.cached(timeout=60, query_string=True)
    def get(user_authenticated):
        page, per_page, offset = get_page_args()

        logs = repository_service_log.get_all()

        pagination_logs = logs[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=len(logs))

        schema_log = schemas.ServiceLogGetSchema(many=True)
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


class LogsRequestsResource(Resource):

    @staticmethod
    @token_provider.verify_token
    @token_provider.admin_required
    def get(user_authenticated):
        page, per_page, offset = get_page_args()

        logs = repository_request_log.get_all()

        pagination_logs = logs[offset: offset + per_page]
        pagination = Pagination(page=page, per_page=per_page, total=len(logs))

        schema_log = schemas.RequestLogGetSchema(many=True)
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
