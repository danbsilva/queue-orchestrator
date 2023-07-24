from functools import wraps
from decouple import config as config_env
from datetime import datetime, timedelta
import jwt
from flask import request
from src.extensions.flask_cache import cache
from src import messages

ACCESS_TOKEN_EXPIRE = 30


def create_token(payload):
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE)
    payload['exp'] = exp

    token = jwt.encode(payload, config_env('SECRET_KEY'), algorithm=config_env('ALGORITHM'))
    if not token:
        return {'message': messages.ERR_TOKEN_GENERATE}, 400

    return token


def verify_token():

    try:
        token = request.headers['Authorization']
    except KeyError:
        return messages.TOKEN_IS_MISSING, 401

    if not token.startswith('Bearer '):
        return messages.INVALID_TOKEN_FORMAT, 401

    token = token.replace('Bearer ', '')

    cache_token = cache.get(f'TOKEN_BLACKLIST_{token}')
    if cache_token:
        return messages.TOKEN_IS_INVALID, 401

    try:
        user_authenticated = jwt.decode(token, config_env('SECRET_KEY'), algorithms=[config_env('ALGORITHM')])
    except Exception:
        return messages.TOKEN_IS_INVALID, 401

    return user_authenticated, 200


def verify_token_email(token):
    try:
        user_authenticated = jwt.decode(token.replace('Bearer ', ''), config_env('SECRET_KEY'), algorithms=[config_env('ALGORITHM')])
    except jwt.InvalidTokenError:
        return {'message': messages.TOKEN_IS_INVALID}, 401

    return user_authenticated


def admin_required(f):
    @wraps(f)
    def decorated(cls, *args, **kwargs):

        if not args[0]['is_admin']:
            return {'message': messages.UNAUTHORIZED_USER}, 401

        return f(cls, *args, **kwargs)
    return decorated