import os
from marshmallow import ValidationError

from flask import request
from flask_restful import Resource
from flask_paginate import Pagination
from werkzeug.exceptions import UnsupportedMediaType

from src.providers import cors_provider
from src.logging import Logger
from src.schemas import automationschemas
from src.models.automationmodel import AutomationModel
from src import messages

import requests


__module_name__ = 'src.controllers.automationcontroller'


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
    

# Function to verify token
def verify_token():
    try:
        response = requests.request('GET', 'http://auth:80/auth/validate/token/',
                                    headers=request.headers)
        if response.status_code != 200:
            Logger().dispatch('INFO', __module_name__, 'verify_token',
                                   f'Error validating token: {response.text}')
            return messages.UNAUTHORIZED, 401
        return response.json(), 200

    except Exception as e:
        Logger().dispatch('INFO', __module_name__, 'verify_token',
                               f'Error validating token: {e}')
        return messages.INTERNAL_SERVER_ERROR, 500


# Function to verify owner exists
def verify_owner_exists(user_uuid):
    try:
        response = requests.request('GET', f'http://auth:80/auth/users/{user_uuid}/',
                                    headers=request.headers)
        if response.status_code != 200:
            Logger().dispatch('INFO', __module_name__, 'verify_user_exists',
                                   f'Error validating user: {response.text}')
            return messages.UNAUTHORIZED, 401
        return response.json(), 200

    except Exception as e:
        Logger().dispatch('INFO', __module_name__, 'verify_user_exists',
                               f'Error validating user: {e}')
        return messages.INTERNAL_SERVER_ERROR, 500


## AUTOMATIONS ##
class AutomationsResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def post():
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'AutomationsResource.post',
                                       f'Error getting data: {e}')
                return {'message': messages.INTERNAL_SERVER_ERROR}, 500

            schema_validate = validate_schema(automationschemas.AutomationPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            if AutomationModel.get_by_name(name=data['name']):
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation name {data["name"]} already exists')
                return {'message': messages.AUTOMATION_NAME_ALREADY_EXISTS}, 400

            if AutomationModel.get_by_acronym(acronym=data['acronym']):
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation acronym {data["acronym"]} already exists')
                return {'message': messages.AUTOMATION_ACRONYM_ALREADY_EXISTS}, 400

            try:
                automation = AutomationModel.create(new_automation=data)
                Logger().dispatch('INFO', __module_name__, 'AutomationsResource.post',
                                       f'Automation {automation.uuid} created successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'AutomationsResource.post',
                                       f'Error creating automation: {e}')
                return {'message': messages.ERROR_CREATING_AUTOMATION}, 400

            schema_automation = automationschemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationsResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get():
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automations = AutomationModel.get_all(search=search)

            pagination_automations = automations[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automations))

            schema_automation = automationschemas.AutomationGetSchema(many=True)
            schema_data = schema_automation.dump(pagination_automations)

            Logger().dispatch('INFO', __module_name__, 'AutomationsResource.get',
                                   f'{str(len(pagination_automations))} automations found')
            return {'automations': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_automations),
                        'offset': offset
                    }}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationsResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class AutomationResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            schema_automation = automationschemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            Logger().dispatch('INFO', __module_name__, 'AutomationResource.get',
                                   f'Automation {schema_data["uuid"]} found')
            return {'automation': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def patch(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(automationschemas.AutomationPatchSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)

            if not automation:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            if data.get('name'):
                if automation.name != data['name']:
                    if AutomationModel.get_by_name(name=data['name']):
                        Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch',
                                               f'Automation name {data["name"]} already exists')
                        return {'message': messages.AUTOMATION_NAME_ALREADY_EXISTS}, 400

            if data.get('acronym'):
                if automation.acronym != data['acronym']:
                    if AutomationModel.get_by_acronym(acronym=data['acronym']):
                        Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch',
                                               f'Automation acronym {data["acronym"]} already exists')
                        return {'message': messages.AUTOMATION_ACRONYM_ALREADY_EXISTS}, 400

            try:
                automation = AutomationModel.update(automation=automation, new_automation=data)
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.patch',
                                        f'Automation {automation.uuid} updated successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'AutomationResource.patch',
                                       f'Error updating automation: {e}')
                return {'message': messages.ERROR_UPDATING_AUTOMATION}, 400

            schema_automation = automationschemas.AutomationGetSchema()
            schema_data = schema_automation.dump(automation)

            return {'automation': schema_data}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationResource.patch', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(automation_uuid):
        try:
            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.delete', f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            try:
                AutomationModel.delete(automation)
                Logger().dispatch('INFO', __module_name__, 'AutomationResource.delete',
                                        f'Automation {automation.uuid} deleted successfully')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'AutomationResource.delete',
                                       f'Error deleting automation: {e}')
                return {'message': messages.ERROR_DELETING_AUTOMATION}, 400

            return {'message': messages.AUTOMATION_DELETED}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class AutomationMeResource(Resource):
    @staticmethod
    @cors_provider.origins_allowed
    def get():
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')
            message, status_code = verify_token()
            if status_code != 200:
                return {'message': message}, status_code

            user_uuid = message['user']['uuid']

            automations = AutomationModel.get_by_owner(owner_uuid=user_uuid, search=search)

            pagination_automations = automations[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(automations))

            schema_automation = automationschemas.AutomationGetSchema(many=True)
            schema_data = schema_automation.dump(pagination_automations)

            Logger().dispatch('INFO', __module_name__, 'AutomationMeResource.get',
                                   f'{str(len(pagination_automations))} automations found for user {user_uuid}')

            return  {'automations': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_automations),
                        'offset': offset
                    }}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'AutomationMeResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500


class OwnersByAutomationResource(Resource):

    @staticmethod
    @cors_provider.origins_allowed
    def post(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(automationschemas.OwnerPostSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owner = data
            response, code = verify_owner_exists(owner['uuid'])
            if code != 200:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Owner {owner["uuid"]} not found')
                return {'message': messages.OWNER_NOT_FOUND}, 404

            user = response['user']
            if owner["uuid"] in [owner_db['uuid'] for owner_db in automation.owners]:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Owner {owner["uuid"]} already exists in automation {automation.uuid}')

                return {'message': messages.OWNER_ALREADY_EXISTS}, 400

            try:
                AutomationModel.add_owners(automation, user)
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.post',
                                        f'Owner {owner["uuid"]} added to automation {automation.uuid}')

            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'OwnersByAutomationResource.post',
                                       f'Error adding owner {owner["uuid"]} to automation {automation.uuid}: {e}')

            return {'owner': user}, 201

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'OwnersByAutomationResource.post', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def get(automation_uuid):
        try:
            page, per_page, offset = get_page_args()
            search = request.args.get('search')

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owners = AutomationModel.get_owners(automation_uuid=automation_uuid, search=search)

            pagination_owners = owners[offset: offset + per_page]
            pagination = Pagination(page=page, per_page=per_page, total=len(owners))

            schema_data = owners

            Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.get',
                                   f'Owners found for automation {automation_uuid}')
            return {'owners': schema_data,
                    'pagination': {
                        'total_pages': pagination.total_pages,
                        'current_page': page,
                        'per_page': pagination.per_page,
                        'total_items': pagination.total,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev,
                        'total_items_this_page': len(pagination_owners),
                        'offset': offset
                    }}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'OwnersByAutomationResource.get', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

    @staticmethod
    @cors_provider.origins_allowed
    def delete(automation_uuid):
        try:
            try:
                data = request.get_json()
            except UnsupportedMediaType as e:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.delete', str(e))
                return {'message': messages.UNSUPPORTED_MEDIA_TYPE}, 415
            except Exception as e:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.delete', str(e))
                return {'message': messages.BAD_REQUEST}, 400

            schema_validate = validate_schema(automationschemas.OwnerDeleteSchema(), data)
            if schema_validate:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Schema validation error: {schema_validate}')
                return {'message': schema_validate}, 400

            automation = AutomationModel.get_by_uuid(uuid=automation_uuid)
            if not automation:
                Logger().dispatch('INFO', __module_name__, 'OwnerByAutomationResource.delete',
                                       f'Automation {automation_uuid} not found')
                return {'message': messages.AUTOMATION_NOT_FOUND}, 404

            owner = data
            if owner['uuid'] not in [owner_db['uuid'] for owner_db in automation.owners]:
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Owner {owner["uuid"]} not found in automation {automation.uuid}')
                return {'message': messages.OWNER_NOT_FOUND}, 404

            try:
                AutomationModel.remove_owners(automation, owner)
                Logger().dispatch('INFO', __module_name__, 'OwnersByAutomationResource.delete',
                                        f'Owner {owner["uuid"]} removed from automation {automation.uuid}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'OwnersByAutomationResource.delete',
                                       f'Error removing owner {owner["uuid"]} from automation {automation.uuid}: {e}')

            return {'message': messages.OWNER_REMOVED}, 200

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'OwnerByAutomationResource.delete', str(e))
            return {'message': messages.INTERNAL_SERVER_ERROR}, 500

