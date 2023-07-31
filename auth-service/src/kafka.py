import json
from decouple import config as config_env
from src import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

__module_name__ = 'src.kafka'

def kafka_producer(topic, key, value):

    try:
        producer = KafkaProducer(bootstrap_servers=config_env('KAFKA_SERVER'),
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, key=key.encode('utf-8'), value=value)
        producer.flush()
        producer.close()
    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'kafka_producer',
                               f'Error on send message to kafka: {e}')
