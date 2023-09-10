import os
import requests
from flask import session, request

service_url = 'automations/'

def get_headers():
    headers = dict(request.headers)
    headers['X-TRANSACTION-ID'] = request.transaction_id
    headers['Authorization'] = f'{session["token"]}' if 'token' in session else None
    headers['Content-Type'] = 'application/json'

    return headers


# AUTOMATIONS
def automations(page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar automações'}, 500


def my_automations(page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}me/?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar automações'}, 500

def automation(uuid):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao buscar automação'}, 500


def new_automation(data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar automação'}, 500


def edit_automation(uuid, data):
    response = requests.request(
        method='PATCH',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{uuid}/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao editar automação'}, 500


def delete_automation(uuid):
    response = requests.request(
        method='DELETE',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao excluir automação'}, 500


# OWNERS
def owners(automation_uuid, page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/owners/?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar proprietários'}, 500


def new_owner(automation_uuid, data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/owners/',
        headers=get_headers(),
        json=data
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar proprietário'}, 500


def delete_owners(automation_uuid, data):
    response = requests.request(
        method='DELETE',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/owners/',
        json=data,
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao excluir proprietário'}, 500


# STEPS
def steps(automation_uuid, page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/steps/?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar passos'}, 500


def step(uuid):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao buscar passo'}, 500


def new_step(automation_uuid, data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/steps/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar passo'}, 500


def edit_step(uuid, data):
    response = requests.request(
        method='PATCH',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{uuid}/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao editar passo'}, 500


def delete_step(uuid):
    response = requests.request(
        method='DELETE',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao excluir passo'}, 500


# FIELDS
def fields(step_uuid, page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{step_uuid}/fields/?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar campos'}, 500


def field(uuid):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/fields/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao buscar campo'}, 500


def new_field(step_uuid, data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{step_uuid}/fields/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar campo'}, 500


def edit_field(uuid, data):
    response = requests.request(
        method='PATCH',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/fields/{uuid}/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao editar campo'}, 500


def delete_field(uuid):
    response = requests.request(
        method='DELETE',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/fields/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao excluir campo'}, 500


# ITEMS
def items_by_automation(automation_uuid, page, per_page):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/items/?page={page}&per_page={per_page}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar itens'}, 500


def items_by_step(step_uuid, page, per_page, search=''):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{step_uuid}/items/?page={page}&per_page={per_page}&search={search}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar itens'}, 500


def item(uuid):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}items/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao buscar item'}, 500


def new_item_by_automation(automation_uuid, data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}{automation_uuid}/items/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar item'}, 500


def new_item_by_step(step_uuid, data):
    response = requests.request(
        method='POST',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}steps/{step_uuid}/items/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao criar item'}, 500


def edit_item(uuid, data):
    response = requests.request(
        method='PATCH',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}items/{uuid}/',
        headers=get_headers(),
        json=data

    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao editar item'}, 500


def delete_item(uuid):
    response = requests.request(
        method='DELETE',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}items/{uuid}/',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao excluir item'}, 500



# HISTORIC
def historic(item_uuid, page, per_page):
    response = requests.request(
        method='GET',
        url=f'http://{os.getenv("GATEWAY_HOST")}{service_url}items/{item_uuid}/historic/?page={page}&per_page={per_page}',
        headers=get_headers()
    )
    try:
        return response.json(), response.status_code
    except:
        return {'message': 'Erro ao listar histórico'}, 500
