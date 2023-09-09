import requests
from decouple import config as config_env
from flask import session

service_url = 'auth/'


def login(email, password):
    response = requests.post(
        f'http://{config_env("GATEWAY_HOST")}{service_url}login/',
        data={
            'email': email,
            'password': password
        }
    )
    try:
        return response.json(), response.status_code
    except:
        return {message: 'Erro ao fazer login'}, 500


def logout():
    response = requests.post(
        f'http://{config_env("GATEWAY_HOST")}{service_url}logout/',
        headers={
            'Authorization': f'{session["token"]}'
        }
    )
    try:
        return response.json(), response.status_code
    except:
        return {message: 'Erro ao fazer logout'}, 500