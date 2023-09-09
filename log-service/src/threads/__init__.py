
import os
from threading import Thread
from src.services.kafkaservice import KafkaService
from src import callbacks

def execute(app):

    # Thread to consumer topic SERVICES LOGS
    Thread(target=KafkaService().consumer, args=(
        app, 
        os.getenv('TOPIC_SERVICES_LOGS'), 
        callbacks.save_service,)
    ).start()

    # Thread to consumer topic REQUESTS LOGS
    Thread(target=KafkaService().consumer, args=(
        app, 
        os.getenv('TOPIC_REQUESTS_LOGS'), 
        callbacks.save_request,)
    ).start()
