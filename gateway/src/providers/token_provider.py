import requests
from flask import request
from src import messages
from src import logging
from src import models

__module_name__ = 'src.providers.token_provider'

ACCESS_TOKEN_EXPIRE = 30


def token_required():

    auth = models.Service.query.filter_by(service_name='auth').first()
    if not auth:
        logging.send_log_kafka('INFO', __name__, 'token_required', messages.SERVICE_AUTH_NOT_FOUND)
        return {'message': messages.SERVICE_AUTH_NOT_FOUND}, 404

    try:
        request.headers['Authorization']
    except KeyError:
        logging.send_log_kafka('INFO', __name__, 'token_required', messages.TOKEN_IS_MISSING)
        return {'message': messages.TOKEN_IS_MISSING}, 401

    headers = dict(request.headers)
    headers['X-TRANSACTION-ID'] = request.transaction_id

    url = f'{auth.service_host}/{auth.service_name}/token/validate/'
    try:
        response = requests.request(
            method='GET',
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        logging.send_log_kafka('CRITICAL', __module_name__, 'token_required', e.args[0])
        return {'message': messages.SERVICE_UNAVAILABLE}, 503



def admin_required():
    auth = models.Service.query.filter_by(service_name='auth').first()
    if not auth:
        logging.send_log_kafka('INFO', __name__, 'admin_required', messages.SERVICE_AUTH_NOT_FOUND)
        return {'message': messages.SERVICE_AUTH_NOT_FOUND}, 404

    try:
        request.headers['Authorization']
    except KeyError:
        logging.send_log_kafka('INFO', __name__, 'admin_required', messages.TOKEN_IS_MISSING)
        return {'message': messages.TOKEN_IS_MISSING}, 401

    headers = dict(request.headers)
    headers['X-TRANSACTION-ID'] = request.transaction_id


    url = f'{auth.service_host}/{auth.service_name}/admin/validate/'
    try:
        response = requests.request(
            method='GET',
            url=url,
            headers=headers,
            params=request.args,
            data=request.get_data(),
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        logging.send_log_kafka('CRITICAL', __module_name__, 'admin_required', e.args[0])
        return {'message': messages.SERVICE_UNAVAILABLE}, 503