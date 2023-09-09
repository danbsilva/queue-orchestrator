import os
from threading import Thread

from src.services.kafkaservice import KafkaService
from src import callbacks


def execute(app):

    # Threads to consumer topics and send email validation to user register
    Thread(target=KafkaService().consumer, args=(
        app, 
        os.getenv('TOPIC_SEND_EMAIL_VALIDATION_ACCOUNT'), 
        callbacks.send_mail,)
    ).start()

    # Threads to consumer topics and send email recovery password to user
    Thread(target=KafkaService().consumer, args=(
        app, 
        os.getenv('TOPIC_SEND_EMAIL_RECOVERY_PASSWORD'), 
        callbacks.send_mail,)
    ).start()

    