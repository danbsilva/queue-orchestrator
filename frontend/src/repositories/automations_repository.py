import requests
from decouple import config as config_env
from flask import session, request

service_url = 'auth/'

def headers():
    headers = dict(request.headers)
    headers['X-TRANSACTION-ID'] = request.transaction_id
    headers['Authorization'] = f'{session["token"]}' if 'token' in session else None
    headers['Content-Type'] = 'application/json'

    return headers

def login(email, password):
    payload = {
            'email': email,
            'password': password
        }
    response = requests.request(
        method='POST',
        url=f'http://{config_env("GATEWAY_HOST")}{service_url}login/',
        json=payload,
        headers=headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao fazer login'}, 500


def logout():
    response = requests.request(
        method='POST',
        url=f'http://{config_env("GATEWAY_HOST")}{service_url}logout/',
        headers=headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao fazer logout'}, 500


def verify_token():
    response = requests.request(
        method='GET',
        url=f'http://{config_env("GATEWAY_HOST")}{service_url}validate/token/',
        headers=headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao verificar token'}, 500