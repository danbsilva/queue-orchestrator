import os
import time
import uuid
from datetime import datetime
from threading import Thread

from flask import request, redirect
from src.services.kafkaservice import KafkaService



def load(app):
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
            'service': os.getenv('APP_NAME'),
            'transaction_id': request.transaction_id,
            'ip': request.remote_addr,
            'method': request.method,
            'endpoint': request.url_rule.rule if request.url_rule else 'NOT_FOUND',
            'params': ', '.join(str(value) for value in list(request.view_args.values())) if request.view_args else '',
            'status': response.status_code,
            'duration': time.time() - request.start_time
        }

        Thread(target=KafkaService().producer, args=(os.getenv('TOPIC_REQUESTS_LOGS'), os.getenv('APP_NAME'), payload,)).start()

        return response