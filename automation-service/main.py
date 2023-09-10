import os
from threading import Thread
from dotenv import load_dotenv

load_dotenv('.env')
load_dotenv('shared.env')


from src import app, register, callbacks
from src.services.kafkaservice import KafkaService


main_app = app.create_app()

# Register service in API Gateway
register.service(app=main_app)

# Thread to consumer topic PROCESSED_ITEMS
Thread(target=KafkaService().consumer, args=(main_app, os.getenv('TOPIC_PROCESSED_ITEMS'), callbacks.items_processed,)).start()

# Thread to consumer topic ITEMS_IN_PROCESS
Thread(target=KafkaService().consumer, args=(main_app, os.getenv('TOPIC_ITEMS_IN_PROCESS'), callbacks.items_in_process,)).start()


if __name__ == '__main__':

    host = os.getenv("APP_HOST")
    port = os.getenv("APP_PORT")
    debug = os.getenv("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
