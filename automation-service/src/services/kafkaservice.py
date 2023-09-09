import json
from decouple import config as config_env
from time import sleep
from src import logging

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic
from threading import Thread

__module_name__ = 'src.kafka'


def is_broker_available():
    try:
        KafkaConsumer(bootstrap_servers=config_env('KAFKA_SERVER'))
        return True
    except KafkaError:
        return False


def wait_for_broker():
    while not is_broker_available():
        sleep(1)


def create_topic(topic_name, num_partitions, replication_factor, transaction_id=None):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

        topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        if topic_name not in admin_client.list_topics():
            # Create topic
            admin_client.create_topics([topic])
            logging.send_log_kafka('INFO', __module_name__, 'create_topic',
                                   f'Topic {topic_name} created', transaction_id)
        else:
            logging.send_log_kafka('INFO', __module_name__, 'create_topic',
                                   f'Topic {topic_name} already exists', transaction_id)
    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'create_topic',
                                 f'Error creating topic {topic_name}: {str(e)}', transaction_id)


def rename_topic(old_topic, new_topic, transaction_id=None):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

        # Cria um novo tópico com o novo nome
        create_topic(new_topic, 1, 1, transaction_id)

        # Verifica se o tópico antigo existe
        if old_topic in admin_client.list_topics():

            # Copia as mensagens do tópico antigo para o novo tópico
            consumer = KafkaConsumer(
                                    bootstrap_servers=config_env('KAFKA_SERVER'),
                                    group_id='automation_service_group',
                                    auto_offset_reset='earliest'
                                    )

            consumer.subscribe([old_topic])

            messages = consumer.poll(0.5)
            while messages:
                for message in messages[old_topic]:
                    kafka_producer(new_topic, message.key, message.value)
                messages = consumer.poll(0.5)

            logging.send_log_kafka('INFO', __module_name__, 'rename_topic',
                                        f'Messages from topic {old_topic} copied to {new_topic}', transaction_id)

            consumer.close()

            # Exclui o tópico antigo
            delete_topic(old_topic, transaction_id)

        else:
            logging.send_log_kafka('INFO', __module_name__, 'rename_topic',
                                     f'Old topic {old_topic} does not exists', transaction_id)

        logging.send_log_kafka('INFO', __module_name__, 'rename_topic',
                                   f'Topic {old_topic} renamed to {new_topic}', transaction_id)

    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'rename_topic',
                                 f'Error renaming topic {old_topic} to {new_topic}: {str(e)}', transaction_id)


def delete_topic(topic_name, transaction_id=None):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

        # Delete topic
        admin_client.delete_topics([topic_name])
        logging.send_log_kafka('INFO', __module_name__, 'delete_topic',
                               f'Topic {topic_name} deleted', transaction_id)
    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'delete_topic',
                               f'Erorr deleting topic {topic_name}: {str(e)}', transaction_id)


def kafka_producer(topic, key, value):

    try:
        producer = KafkaProducer(bootstrap_servers=config_env('KAFKA_SERVER'),
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, key=key.encode('utf-8'), value=value)
        producer.flush()
        producer.close()
    except KafkaError as e:
        logging.send_log_kafka('ERROR', __module_name__, 'kafka_producer',
                                 f'Error sending message to topic {topic}: {str(e)}')


def kafka_consumer(app, topic, callback):
    wait_for_broker()
    try:
        consumer = KafkaConsumer(bootstrap_servers=config_env('KAFKA_SERVER'),
                                 group_id='automation_service_group'
                                 )

        consumer.subscribe([topic])

        for message in consumer:
            consumer.poll(0.5)
            key = message.key.decode('utf-8')
            msg = json.loads(message.value.decode('utf-8'))
            callback(app, key, msg)

    except KafkaError as e:
        logging.send_log_kafka('ERROR', __module_name__, 'kafka_consumer',
                                 f'Error consuming message from topic {topic}: {str(e)}')
