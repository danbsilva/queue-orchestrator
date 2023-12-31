from decouple import config as config_env
from threading import Thread
from src import app, kafka, register, callbacks


main_app = app.create_app()

# Register service in API Gateway
register.register_service(app=main_app)

# Thread to consumer topic PROCESSED_ITEMS
Thread(target=kafka.kafka_consumer, args=(main_app, config_env('TOPIC_PROCESSED_ITEMS'), callbacks.items_processed,)).start()

# Thread to consumer topic ITEMS_IN_PROCESS
Thread(target=kafka.kafka_consumer, args=(main_app, config_env('TOPIC_ITEMS_IN_PROCESS'), callbacks.items_in_process,)).start()


if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
