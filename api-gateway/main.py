from threading import Thread
from decouple import config as config_env

from src import app, kafka, callbacks
#from src import check_microservice_availability

app = app.create_app()


if __name__ == '__main__':

    #Thread(target=check_microservice_availability.run_scheduler, args=(app,)).start()

    Thread(target=kafka.kafka_consumer, args=(app, 'SERVICES_REGISTER', callbacks.service_register, )).start()

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")

    app.run(host=host, port=port, debug=debug, use_reloader=debug)
else:
    gunicorn_app = app
