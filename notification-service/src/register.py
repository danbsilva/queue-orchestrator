from decouple import config as config_env
from threading import Thread

from src import kafka


def register_service(app):
    with app.app_context():
        service_name = app.name
        service_host = f'http://{config_env("CONTAINER_NAME")}:{config_env("APP_PORT")}'
        routes = register_routes(app)

        data = {
            'service_name': service_name,
            'service_host': service_host,
            'routes': routes
        }

        Thread(target=kafka.kafka_producer, args=('SERVICES_REGISTER', app.name, data, )).start()


def register_routes(app):
    routes = extract_routes(app)
    routes_list = []
    for route in routes:
        endpoint = route['path']
        args = route['args'] if route['args'] else ''
        methods_allowed = route['methods']
        requires_auth = True

        data = {
            'route': endpoint,
            'args': args,
            'methods_allowed': methods_allowed,
            'required_auth': requires_auth
        }
        routes_list.append(data)

    return routes_list


def extract_routes(app):
    routes = []

    for rule in app.url_map.iter_rules():
        # Ignore static routes and 404 error handler
        if '404' in rule.endpoint or 'static' in rule.endpoint:
            continue

        # Extract the methods of the route
        path = rule.rule
        methods = rule.methods
        endpoint = app.view_functions[rule.endpoint]
        methods = [method for method in methods if method != 'OPTIONS' and method != 'HEAD' and method != 'TRACE']

        # Create the route
        route = {
            'path': path,
            'args': '{args}'.format(args='>'.join(rule.arguments)),
            'methods': methods,
            'endpoint': endpoint.__name__,
        }

        routes.append(route)

    return routes
