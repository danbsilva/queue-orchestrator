from datetime import datetime
from decouple import config as config_env
from threading import Thread

from flask import request

from src import kafka


def send_log_kafka(level, module_name, function_name, message, transaction_id=None):

    if not transaction_id:
        try:
            transaction_id = request.headers.get('X-TRANSACTION-ID')
        except RuntimeError:
            transaction_id = ''

    log = {'datetime': str(datetime.now()),
           'level': level,
           'service_name': config_env('APP_NAME'),
           'transaction_id': transaction_id,
           'module_name': module_name,
           'function_name': function_name,
           'message': message}

    Thread(target=kafka.kafka_producer, args=('SERVICES_LOGS', config_env('APP_NAME'), log,)).start()
