import json
import os

from kafka import KafkaProducer
from kafka.errors import KafkaError

class KafkaService:

    default_config = {
         'bootstrap_servers': os.getenv('KAFKA_SERVER'),
    }

    config_producer = {
        'value_serializer': lambda v: json.dumps(v).encode('utf-8')
    }

    def producer(self, topic, key, value):
        try:
            config = {**self.default_config, **self.config_producer}
            kafka_producer = KafkaProducer(**config)
            kafka_producer.send(topic, key=key.encode('utf-8'), value=value)
            kafka_producer.flush()
            kafka_producer.close()
        except KafkaError as e:
            print(f'Error on send message to kafka: {e}')
