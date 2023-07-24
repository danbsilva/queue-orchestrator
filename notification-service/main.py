from decouple import config as config_env
from src import threads, register

from src import app, kafka, callbacks

app = app.create_app()

register.register_service(app=app)

# Threads to consumer topics and send email validation to user register
threads.start_thread(target=kafka.kafka_consumer,
                     args=(app, config_env('TOPIC_SEND_EMAIL_VALIDATION'), callbacks.send_mail,))


if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")

    app.run(host=host, port=port, debug=debug, use_reloader=debug)
else:
    gunicorn_app = app
