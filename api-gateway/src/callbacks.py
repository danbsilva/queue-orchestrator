import json
from datetime import datetime
from threading import Thread

from src import repository_service_routes, kafka
from src import repository_service


def service_register(app, key, msg):
    with app.app_context():
        try:
            data_service = json.loads(json.dumps(msg))
            del data_service['routes']

            service = repository_service.get_by_service_name(service_name=data_service['service_name'])
            if not service:
                service = repository_service.create(new_service=data_service)
            else:
                repository_service.update(service=service, new_service=data_service)

            if service:

                data_routes = msg['routes']

                for route in data_routes:
                    route_db = repository_service_routes.get_by_service_id_and_route(service_id=service.id,
                                                                                     route=route['route'])
                    if route_db:
                        repository_service_routes.update(service_route=route_db, new_service_route=route)
                    else:
                        repository_service_routes.create(service=service, new_service_route=route)

        except Exception as e:
            log = {
                'datetime': str(datetime.now()),
                'level': 'CRITICAL',
                'service_name': 'api-gateway',
                'module_name': 'src.callbacks',
                'function_name': 'service_register',
                'message': e.args[0]
            }
            Thread(target=kafka.kafka_producer, args=('LOGS', 'api-gateway', log,)).start()
