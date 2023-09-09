import os

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from src.docs import logs


__module_name__ = 'src.controllers.swaggercontroller'


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

class SwaggerResource(Resource):
    def get(self):
        return logs.doc_swagger
