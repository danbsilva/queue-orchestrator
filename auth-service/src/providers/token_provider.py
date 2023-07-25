from functools import wraps
from decouple import config as config_env
from datetime import datetime, timedelta
import jwt
from flask import request
from src.extensions.flask_cache import cache
from src import messages
from src import models
from src import logging

__module_name__ = 'src.providers.token_provider'


ACCESS_TOKEN_EXPIRE = 30


def create_token(payload):
    exp = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE)
    payload['exp'] = exp

    token = jwt.encode(payload, config_env('SECRET_KEY'), algorithm=config_env('ALGORITHM'))
    if not token:
        logging.send_log_kafka('INFO', __module_name__, 'create_token',
                               'Error token generate')
        return {'message': messages.ERR_TOKEN_GENERATE}, 400

    return token


def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers['Authorization']
        except KeyError:
            logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                   'Token is missing')
            return {'message': messages.TOKEN_IS_MISSING}, 401

        if not token.startswith('Bearer '):
            logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                   'Token used is invalid format')
            return {'message': messages.INVALID_TOKEN_FORMAT}, 401

        token = token.replace('Bearer ', '')

        cache_token = cache.get(f'BLACKLIST_TOKEN_{token}')
        if cache_token:
            logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                   'Token used is blacklist')
            return {"message": messages.TOKEN_IS_INVALID}, 401

        try:
            user_authenticated = jwt.decode(token, config_env('SECRET_KEY'), algorithms=[config_env('ALGORITHM')])
            user_db = models.User.query.filter_by(uuid=user_authenticated['uuid']).first()
            if not user_db:
                logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                       'Token used is unauthorized')
                return {'message': messages.UNAUTHORIZED_USER}, 401
        except Exception:
            logging.send_log_kafka('INFO', __module_name__, 'verify_token',
                                   'Token used is invalid')
            return {'message': messages.TOKEN_IS_INVALID}, 401

        return f(user_authenticated, *args, **kwargs)

    return decorated


def verify_token_email(token):
    try:
        user_authenticated = jwt.decode(token.replace('Bearer ', ''), config_env('SECRET_KEY'),
                                        algorithms=[config_env('ALGORITHM')])
    except jwt.InvalidTokenError:
        logging.send_log_kafka('INFO', __module_name__, 'verify_token_email',
                               'Token used is invalid')
        return {'message': messages.TOKEN_IS_INVALID}, 401

    return user_authenticated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if not args[0]['is_admin']:
            logging.send_log_kafka('INFO', __module_name__, 'admin_required',
                                   'User unauthorized')
            return {'message': messages.UNAUTHORIZED_USER}, 401

        return f(*args, **kwargs)
    return decorated
