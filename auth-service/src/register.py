from decouple import config as config_env
from threading import Thread
from src import kafka
from src.docs import auth


def filter_endpoint(endpoint_path, method, schema):
    filtered_endpoints = list(filter(lambda x: x['endpoint'] == endpoint_path, auth.docs_endpoints))

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

        Thread(target=kafka.kafka_producer, args=(config_env('TOPIC_SERVICES_REGISTER'), app.name, data, )).start()


def register_routes(app):
    routes = extract_routes(app)
    routes_list = []
    for route in routes:
        endpoint = route['path']
        args = route['args'] if route['args'] else ''
        methods_allowed = route['methods']

        if ('login' in endpoint or 'validate-email' in endpoint or 'send-email-validation' in endpoint
                or 'forgot-password' in endpoint or 'reset-password' in endpoint):
            required_auth = False
        else:
            required_auth = True

        data = {
            'route': endpoint,
            'args': args,
            'methods_allowed': methods_allowed,
            'required_auth': required_auth,
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
