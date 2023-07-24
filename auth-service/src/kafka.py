import json
from decouple import config as config_env

from kafka import KafkaProducer
from kafka.errors import KafkaError


def kafka_producer(topic, key, value):

    try:
        producer = KafkaProducer(bootstrap_servers=config_env('KAFKA_SERVER'),
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, key=key.encode('utf-8'), value=value)
        producer.flush()
        producer.close()
    except KafkaError as e:
        print(f'Error sending message to kafka: {e}')
