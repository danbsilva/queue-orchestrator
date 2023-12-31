from decouple import config as config_env
from src import threads, register

from src import app, kafka, callbacks


main_app = app.create_app()

# Register service in API Gateway
register.register_service(app=main_app)

# Threads to consumer topics and send email validation to user register
threads.start_thread(target=kafka.kafka_consumer,
                     args=(main_app, config_env('TOPIC_SEND_EMAIL_VALIDATION_ACCOUNT'), callbacks.send_mail,))

# Threads to consumer topics and send email recovery password to user
threads.start_thread(target=kafka.kafka_consumer,
                     args=(main_app, config_env('TOPIC_SEND_EMAIL_RECOVERY_PASSWORD'), callbacks.send_mail,))

if __name__ == '__main__':

    host = config_env("APP_HOST")
    port = config_env("APP_PORT")
    debug = config_env("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)
