from decouple import config as config_env
from threading import Thread
from src import kafka, callbacks
from src import app

app = app.create_app()

# Thread to consumer topic SERVICES REGISTER
Thread(target=kafka.kafka_consumer, args=(app, 'SERVICES_REGISTER', callbacks.service_register,)).start()


if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
else:

    gunicorn_app = app