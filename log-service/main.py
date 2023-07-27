from decouple import config as config_env

from src import kafka, callbacks, register
from src import app
from threading import Thread

main_app = app.create_app()

# Register service in API Gateway
register.register_service(app=main_app)

# Thread to consumer topic SERVICES LOGS
Thread(target=kafka.kafka_consumer, args=(main_app, 'SERVICES_LOGS', callbacks.save_service_log,)).start()

# Thread to consumer topic REQUESTS LOGS
Thread(target=kafka.kafka_consumer, args=(main_app, 'REQUESTS_LOGS', callbacks.save_request_log,)).start()


if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
