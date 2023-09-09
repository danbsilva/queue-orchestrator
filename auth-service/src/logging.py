from datetime import datetime
import os
from threading import Thread
from flask import request

from src.services.kafkaservice import KafkaService


class Logger:

    @staticmethod
    def dispatch(level, module_name, function_name, message):
        log = {'datetime': str(datetime.now()),
               'level': level,
               'service_name': os.getenv('APP_NAME'),
               'transaction_id': request.headers.get('X-TRANSACTION-ID'),
               'module_name': module_name,
               'function_name': function_name,
               'message': message}

        Thread(target=KafkaService().producer, args=(os.getenv('TOPIC_SERVICES_LOGS'), os.getenv('APP_NAME'), log,)).start()
