from decouple import config as config_env

from src import kafka, threads, callbacks, register
from src import app

app = app.create_app()

register.register_service(app=app)

# Threads
# Thread to consumer topic LOGS
threads.start_thread(target=kafka.kafka_consumer, args=(app, 'SERVICES_LOGS', callbacks.save_service_log,))

# Thread to consumer topic REQUESTS LOGS
threads.start_thread(target=kafka.kafka_consumer, args=(app, 'REQUESTS_LOGS', callbacks.save_request_log,))


if __name__ == '__main__':
    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")

    app.run(host=host, port=port, debug=debug, use_reloader=debug)
else:
    gunicorn_app = app
