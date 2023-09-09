import os
from datetime import datetime
from threading import Thread
from uuid import uuid4

from flask import request

from src.services.kafkaservice import KafkaService


class Logger:

    def dispatch(self, level, module_name, function_name, message, transaction_id=None):
        if not transaction_id:
            try:
                transaction_id = request.transaction_id
            except Exception:
                transaction_id = str(uuid4())

        log = {'datetime': str(datetime.now()),
            'level': level,
            'service_name': os.getenv('APP_NAME'),
            'transaction_id': transaction_id,
            'module_name': module_name,
            'function_name': function_name,
            'message': message}
        
        Thread(target=KafkaService().producer, args=(os.getenv('TOPIC_SERVICES_LOGS'), os.getenv('APP_NAME'), log,)).start()
