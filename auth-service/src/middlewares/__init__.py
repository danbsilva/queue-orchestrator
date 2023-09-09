import os
import time
from datetime import datetime
from decouple import config as config_env
from threading import Thread

from flask import request

from src.services.kafkaservice import KafkaService


def load(app):

    @app.route('/health/')
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

        Thread(target=KafkaService().producer, args=(config_env('TOPIC_REQUESTS_LOGS'), config_env('APP_NAME'), payload,)).start()

        return response