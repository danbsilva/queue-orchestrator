from datetime import datetime
from decouple import config as config_env
from threading import Thread

from flask import request
from src import kafka


def send_log_kafka(level, module_name, function_name, message):
    log = {'datetime': str(datetime.now()),
           'level': level,
           'service_name': config_env('APP_NAME'),
           'transaction_id': request.transaction_id,
           'module_name': module_name,
           'function_name': function_name,
           'message': message}
    Thread(target=kafka.kafka_producer, args=('SERVICES_LOGS', config_env('APP_NAME'), log,)).start()
