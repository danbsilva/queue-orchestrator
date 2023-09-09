import json
import os
from time import sleep

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic

class KafkaService:

    default_config = {
        'bootstrap_servers': os.getenv('KAFKA_SERVER'),
    }

    config_producer = {
        'value_serializer': lambda v: json.dumps(v).encode('utf-8')
    }

    config_consumer = {
        'group_id': 'gateway_group',
        'auto_offset_reset': 'earliest'
    }


    def is_broker_available(self):
        try:
            config = {**self.default_config}
            consumer = KafkaConsumer(**config)
            return True
        except KafkaError:
            return False


    def wait_for_broker(self):
        while not self.is_broker_available():
            sleep(1)


    def create_topic(self, topic_name, num_partitions, replication_factor):
        try:
            config = {**self.default_config}

            admin_client = KafkaAdminClient(**config)

            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)

            # Criação do tópico
            admin_client.create_topics([topic])

            print(f"Tópico '{topic_name}' criado com sucesso!")

        except KafkaError as e:
            print(f'Erro ao criar o tópico: {str(e)}')

    def producer(self, topic, key, value):

        try:
            config = {**self.default_config, **self.config_producer}
            producer = KafkaProducer(**config)
            producer.send(topic, key=key.encode('utf-8'), value=value)
            producer.flush()
            producer.close()
        except KafkaError as e:
            print(f'Erro ao enviar a mensagem: {str(e)}')


    def consumer(self, app, topic, callback):
        self.wait_for_broker()
        try:
            config = {**self.default_config, **self.config_consumer}
            consumer = KafkaConsumer(**config)

            consumer.subscribe([topic])

            for message in consumer:
                consumer.poll(0.5)
                key = message.key.decode('utf-8')
                msg = json.loads(message.value.decode('utf-8'))
                callback(app, key, msg)

        except KafkaError as e:
            print(f'Erro ao enviar a mensagem: {str(e)}')


