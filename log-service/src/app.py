import os
import time
from datetime import datetime
from decouple import config as config_env
from threading import Thread

from flask import Flask, request
from src import config, kafka

settings = os.path.join(os.path.dirname(__file__), 'settings.py')

def minimal_app():
    app = Flask(config_env('APP_NAME'))
    app.config.from_pyfile(settings)
    config.init_app(app=app)
    return app


def create_app():
    app = minimal_app()

    @app.route('/health/', methods=['GET'])
    def health():
        return 'OK'

    @app.before_request
    def start_timer():
        request.start_time = time.time()

    @app.after_request
    def register_request_log(response):
        if request.endpoint == 'health':
            return response

        payload = {
            'datetime': str(datetime.now()),
            'service': app.name,
            'transaction_id': request.headers.get('X-TRANSACTION-ID'),
            'ip': request.remote_addr,
            'method': request.method,
            'endpoint': request.url_rule.rule if request.url_rule else 'NOT_FOUND',
            'params': ', '.join(str(value) for value in list(request.view_args.values())) if request.view_args else '',
            'status': response.status_code,
            'duration': time.time() - request.start_time
        }

        Thread(target=kafka.kafka_producer, args=(config_env('TOPIC_REQUESTS_LOGS'), app.name, payload,)).start()

        return response

    return app
