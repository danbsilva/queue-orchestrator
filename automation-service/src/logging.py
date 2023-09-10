import os

from datetime import datetime
from threading import Thread
from flask import request

from src.services.kafkaservice import KafkaService


class Logger:

    @staticmethod
    def dispatch(level, module_name, function_name, message, transaction_id=None):
        if not transaction_id:
            try:
                transaction_id = request.headers.get('X-TRANSACTION-ID')
            except RuntimeError:
                transaction_id = ''

        log = {'datetime': str(datetime.now()),
               'level': level,
               'service_name': os.getenv('APP_NAME'),
               'transaction_id':transaction_id,
               'module_name': module_name,
               'function_name': function_name,
               'message': message}

        Thread(target=KafkaService().producer, args=(os.getenv('TOPIC_SERVICES_LOGS'), os.getenv('APP_NAME'), log,)).start()
