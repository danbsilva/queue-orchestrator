import os
import time
from datetime import datetime
from threading import Thread
from decouple import config as config_env

from flask import Flask, request, redirect
from src import config, kafka
import uuid

settings = os.path.join(os.path.dirname(__file__), 'settings.py')


def minimal_app():
    app = Flask(config_env('APP_NAME'))
    app.config.from_pyfile(settings)
    config.init_app(app=app)
    return app


def create_app():
    app = minimal_app()

    # Redirect to webui
    @app.route('/', methods=['GET'])
    @app.route('/webui/', methods=['GET'])
    @app.route('/webui', methods=['GET'])
    @app.route('/auth/', methods=['GET'])
    @app.route('/auth', methods=['GET'])
    def index():
        return redirect('/webui/home')

    @app.route('/health/', methods=['GET'])
    def health():
        return 'OK'

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
        if 'health' in request.endpoint or 'static' in request.url_rule.rule or 'js' in request.url_rule.rule:
            return response

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

        Thread(target=kafka.kafka_producer, args=(config_env('TOPIC_REQUESTS_LOGS'), app.name, payload,)).start()

        return response

    return app
