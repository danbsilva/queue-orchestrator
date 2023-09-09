import os
from functools import wraps
from flask import request
from src import messages

__module_name__ = 'src.providers.cors_provider'

def origins_allowed(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            origin = request.headers.get('X-ORIGIN')

            if not origin:
                return {'message': messages.ORIGIN_NOT_ALLOWED}, 403

            if origin not in os.getenv('ALLOWED_ORIGINS'):
                return {'message': messages.ORIGIN_NOT_ALLOWED}, 403
        except KeyError:
            return {'message': messages.ORIGIN_NOT_ALLOWED}, 403

        return f(*args, **kwargs)

    return decorated
