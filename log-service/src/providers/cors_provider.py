from functools import wraps
from decouple import config as config_env
from flask import request
from src import messages
from src import logging

__module_name__ = 'src.providers.cors_provider'



def origins_allowed(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            origin = request.headers.get('X-ORIGIN')

            if not origin:
                logging.send_log_kafka('INFO', __module_name__, 'origins_allowed',
                                       messages.ORIGIN_NOT_ALLOWED)
                return {'message': messages.ORIGIN_NOT_ALLOWED}, 403

            if origin not in config_env('ALLOWED_ORIGINS'):
                logging.send_log_kafka('INFO', __module_name__, 'origins_allowed',
                                        messages.ORIGIN_NOT_ALLOWED)
                return {'message': messages.ORIGIN_NOT_ALLOWED}, 403
        except KeyError:
            logging.send_log_kafka('INFO', __module_name__, 'origins_allowed',
                                    messages.ORIGIN_NOT_ALLOWED)
            return {'message': messages.ORIGIN_NOT_ALLOWED}, 403

        return f(*args, **kwargs)

    return decorated
