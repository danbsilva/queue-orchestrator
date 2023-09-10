import os
import json
from time import sleep

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError


class KafkaService:

    default_config = {
        'bootstrap_servers': os.getenv('KAFKA_SERVER'),
    }

    config_producer = {
        'value_serializer': lambda v: json.dumps(v).encode('utf-8')
    }

    config_consumer = {
        'group_id': os.getenv('APP_NAME'),
    }

    def is_broker_available(self):
        try:
            config = {**self.default_config}
            KafkaConsumer(**config)
            return True
        except KafkaError:
            return False

    def wait_for_broker(self):
        while not self.is_broker_available():
            sleep(1)

    def producer(self, topic, key, value):
        try:
            config = {**self.default_config, **self.config_producer}
            kafka_producer = KafkaProducer(**config)
            kafka_producer.send(topic, key=key.encode('utf-8'), value=value)
            kafka_producer.flush()
            kafka_producer.close()
        except KafkaError as e:
            print(f'Error on send message to kafka: {e}')

    def consumer(self, app, topic, callback):
        config = {**self.default_config, **self.config_consumer}
        self.wait_for_broker()
        try:
            kafka_consumer = KafkaConsumer(**config)
            kafka_consumer.subscribe([topic])

            for message in kafka_consumer:
                kafka_consumer.poll(1)
                key = message.key.decode('utf-8')
                msg = json.loads(message.value.decode('utf-8'))
                callback(app, key, msg)

        except KafkaError as e:
            print(f'Error consuming message: {str(e)}')

    def create_topic(self, topic_name, num_partitions=3, replication_factor=3, transaction_id=None):
        try:
            config = {**self.default_config}
            admin_client = KafkaAdminClient(**config)

            topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
            if topic_name not in admin_client.list_topics():
                
                # Create topic
                admin_client.create_topics([topic])

        except KafkaError as e:
            print(f'Error creating topic {topic_name}: {str(e)}')

    def rename_topic(self, old_topic, new_topic, transaction_id=None):
        try:
            config = {**self.default_config}
            admin_client = KafkaAdminClient(**config)

            # Cria um novo tópico com o novo nome
            self.create_topic(new_topic, 1, 1, transaction_id)

            # Verifica se o tópico antigo existe
            if old_topic in admin_client.list_topics():

                config = {**self.default_config, **self.config_consumer}
                # Copia as mensagens do tópico antigo para o novo tópico
                consumer = KafkaConsumer(**config)

                consumer.subscribe([old_topic])

                messages = consumer.poll(0.5)
                while messages:
                    for message in messages[old_topic]:
                        self.producer(new_topic, message.key, message.value)
                    messages = consumer.poll(0.5)

                consumer.close()

                # Exclui o tópico antigo
                self.delete_topic(old_topic, transaction_id)

        except KafkaError as e:
            print(f'Error renaming topic {old_topic} to {new_topic}: {str(e)}')

    def delete_topic(self, topic_name, transaction_id=None):
        try:
            config = {**self.default_config}
            admin_client = KafkaAdminClient(**config)

            # Delete topic
            admin_client.delete_topics([topic_name])

        except KafkaError as e:
            print(f'Error deleting topic {topic_name}: {str(e)}')





