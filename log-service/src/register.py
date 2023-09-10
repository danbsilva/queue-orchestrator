import os
from threading import Thread

from src.docs import logs
from src.services.kafkaservice import KafkaService

def filter_endpoint(endpoint_path, method, schema):
    filtered_endpoints = list(filter(lambda x: x['endpoint'] == endpoint_path, logs.docs_endpoints))

    if filtered_endpoints:
        endpoint_info = filtered_endpoints[0]
        method_info = list(filter(lambda x: method in x.keys(), endpoint_info['methods']))
        if method_info:
            method_info = method_info[0][method]
            schema_model = method_info.get(schema, {})
            return schema_model
        else:
            return {}
    else:
        return {}

def service(app):
    with app.app_context():
        service_name = os.getenv("APP_NAME")
        service_host = f'http://{os.getenv("CONTAINER_NAME")}:{os.getenv("APP_PORT")}'
        routes = register_routes(app)

        data = {
            'service_name': service_name,
            'service_host': service_host,
            'routes': routes
        }
        Thread(target=KafkaService().producer, args=(os.getenv('TOPIC_SERVICES_REGISTER'), os.getenv('APP_NAME'), data,)).start()

def register_routes(app):
    routes = extract_routes(app)
    routes_list = []
    for route in routes:
        endpoint = route['path']
        args = route['args'] if route['args'] else ''
        methods_allowed = route['methods']

        data = {
            'route': endpoint,
            'args': args,
            'methods_allowed': methods_allowed
        }
        routes_list.append(data)

    return routes_list

def extract_routes(app):
    routes = []

    #
    for rule in app.url_map.iter_rules():
        # Ignore rules with 'static' in them and rules with '404' in them
        if '404' in rule.endpoint or 'static' in rule.endpoint:
            continue

        # Extract the methods of the route
        path = rule.rule
        methods = rule.methods
        endpoint = app.view_functions[rule.endpoint]
        methods = [method for method in methods if method != 'OPTIONS' and method != 'HEAD' and method != 'TRACE']
        doc = []
        for method in methods:
            method_doc = {}

            if method == 'GET':
                response = filter_endpoint(path, method, 'response')
                method_doc = {"GET": {"response": response}}

            elif method == 'POST':
                request = filter_endpoint(path, method, 'request')
                response = filter_endpoint(path, method, 'response')
                method_doc = {"POST": {"request": request, "response": response}}

            elif method == 'PATCH':
                request = filter_endpoint(path, method, 'request')
                response = filter_endpoint(path, method, 'response')
                method_doc = {"PATCH": {"request": request, "response": response}}

            elif method == 'DELETE':
                response = filter_endpoint(path, method, 'response')
                method_doc = {"DELETE": {"response": response}}

            doc.append(method_doc)

        # Create the route
        route = {
            'path': path,
            'args': '{args}'.format(args='>'.join(rule.arguments)),
            'methods': doc,
            'endpoint': endpoint.__name__,
        }

        routes.append(route)

    return routes
