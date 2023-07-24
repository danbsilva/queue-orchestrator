import time
from datetime import datetime
from threading import Thread
from decouple import config as config_env

from flask import Flask, request
from src import config, kafka
import uuid


def minimal_app():
    app = Flask(config_env('APP_NAME'))
    app.config.from_pyfile('src/settings.py')
    config.init_app(app=app)
    return app


def create_app():
    app = minimal_app()

    @app.get('/')
    def index():
        return {'service': 'api-gateway'}

    @app.before_request
    def add_transaction_id():
        if request.headers.get('X-TRANSACTION-ID'):
            request.transaction_id = request.headers.get('X-TRANSACTION-ID')
        else:
            request.transaction_id = str(uuid.uuid4())

    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def register_request_log(response):

        payload = {
            'datetime': str(datetime.now()),
            'service': app.name,
            'transaction_id': request.transaction_id,
            'ip': request.remote_addr,
            'method': request.method,
            'endpoint': request.url_rule.rule if request.url_rule else 'NOT_FOUND',
            'params': ', '.join(str(value) for value in list(request.view_args.values())) if request.view_args else '',
            'status': response.status_code,
            'duration': time.time() - request.start_time
        }

        Thread(target=kafka.kafka_producer, args=('REQUESTS_LOGS', app.name, payload,)).start()

        return response

    return app
