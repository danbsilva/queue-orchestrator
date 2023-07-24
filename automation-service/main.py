from decouple import config as config_env

from src import kafka, threads, callbacks, register
from src import app


app = app.create_app()

register.register_service(app=app)

# Thread to consumer topic PROCESSED_ITEMS
threads.start_thread(target=kafka.kafka_consumer, args=(app, 'PROCESSED_ITEMS', callbacks.items_processed,))

# Thread to consumer topic ITEMS_IN_PROCESS
threads.start_thread(target=kafka.kafka_consumer, args=(app, 'ITEMS_IN_PROCESS', callbacks.items_in_progress,))

if __name__ == '__main__':
    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")

    app.run(host=host, port=port, debug=debug, use_reloader=debug)
else:
    gunicorn_app = app
