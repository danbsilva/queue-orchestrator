import json
import os
from datetime import datetime
from threading import Thread

from src.models.servicemodel import ServiceModel
from src.models.routemodel import RouteModel
from src.services.kafkaservice import KafkaService

from src.logging import Logger

__module_name__ = 'src.callbacks'


def service_register(app, key, msg):
    with app.app_context():
        try:
            data_service = json.loads(json.dumps(msg))
            del data_service['routes']

            service = ServiceModel.get_by_service_name(service_name=data_service['service_name'])
            if not service:
                service = ServiceModel.create(new_service=data_service)
                Logger().dispatch('INFO', __module_name__, 'service_register', f'Serviço {service.service_name} registrado')
            else:
                ServiceModel.update(service=service, new_service=data_service)
                Logger().dispatch('INFO', __module_name__, 'service_register', f'Serviço {service.service_name} atualizado')

            if service:

                data_routes = msg['routes']

                for route in data_routes:
                    route_db = RouteModel.get_by_service_id_and_route(service_id=service.id, route=route['route'])
                    if route_db:
                        RouteModel.update(route=route_db, new_route=route)
                        Logger().dispatch('INFO', __module_name__, 'service_register', f'Rota {route["route"]} atualizada')
                    else:
                        RouteModel.create(service=service, new_route=route)
                        Logger().dispatch('INFO', __module_name__, 'service_register', f'Rota {route["route"]} registrada')

        except Exception as e:
            Logger().dispatch('CRITICAL', __module_name__, 'service_register', e.args[0])