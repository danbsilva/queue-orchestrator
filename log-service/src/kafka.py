import json
from decouple import config as config_env
from time import sleep

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from kafka.admin import KafkaAdminClient, NewTopic


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
    admin_client = KafkaAdminClient(bootstrap_servers=config_env('KAFKA_SERVER'))

    topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)

    # Create topic
    admin_client.create_topics([topic])

    print(f"Topic {topic_name} created")


def kafka_producer(topic, key, value):

    try:
        producer = KafkaProducer(bootstrap_servers=config_env('KAFKA_SERVER'),
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, key=key.encode('utf-8'), value=value)
        producer.flush()
        producer.close()
    except KafkaError as e:
        print(f'Error producing message: {str(e)}')


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
        print(f'Error consuming message: {str(e)}')
