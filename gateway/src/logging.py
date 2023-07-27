from datetime import datetime
from decouple import config as config_env
from threading import Thread

from flask import request
from src import kafka
from uuid import uuid4


def send_log_kafka(level, module_name, function_name, message, transaction_id=None):
    if not transaction_id:
        try:
            transaction_id = request.transaction_id
        except Exception:
            transaction_id = str(uuid4())

    log = {'datetime': str(datetime.now()),
           'level': level,
           'service_name': config_env('APP_NAME'),
           'transaction_id': transaction_id,
           'module_name': module_name,
           'function_name': function_name,
           'message': message}
    Thread(target=kafka.kafka_producer, args=(config_env('TOPIC_SERVICES_LOGS'), config_env('APP_NAME'), log,)).start()
