import requests
from decouple import config as config_env
from flask import session, request

service_url = 'auth/'

def headers(request):
    headers = dict(request.headers)
    headers['X-TRANSACTION-ID'] = request.transaction_id
    headers['Authorization'] = f'{session["token"]}' if 'token' in session else None
    headers['Content-Type'] = 'application/json'

    return headers


def users():
    response = requests.request(
        method='GET',
        url=f'http://{config_env("GATEWAY_HOST")}{service_url}users/',
        headers=headers(request)
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao fazer login'}, 500


def me():
    response = requests.request(
        method='GET',
        url=f'http://{config_env("GATEWAY_HOST")}{service_url}users/me/',
        headers=headers(request)
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao fazer login'}, 500
