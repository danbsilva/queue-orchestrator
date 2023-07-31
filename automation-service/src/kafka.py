import json
from decouple import config as config_env
from time import sleep
from src import logging

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic


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


def create_topic(topic_name, num_partitions, replication_factor):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

        topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)

        # Create topic
        admin_client.create_topics([topic])
        logging.send_log_kafka('INFO', __module_name__, 'create_topic',
                               f'Topic {topic_name} created')
    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'create_topic',
                                 f'Error creating topic {topic_name}: {str(e)}')


def delete_topic(topic_name):
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

        # Delete topic
        admin_client.delete_topics([topic_name])
        logging.send_log_kafka('INFO', __module_name__, 'delete_topic',
                               f'Topic {topic_name} deleted')
    except KafkaError as e:
        logging.send_log_kafka('INFO', __module_name__, 'delete_topic',
                               f'Erorr deleting topic {topic_name}: {str(e)}')


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
