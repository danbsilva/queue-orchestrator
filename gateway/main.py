import os
from dotenv import load_dotenv
from threading import Thread

# Load project variables
load_dotenv('.env')

# Load shared variables
load_dotenv('shared.env')


from src import callbacks
from src.services.kafkaservice import KafkaService
from src import app



main_app = app.create_app()


# Thread to consumer topic SERVICES REGISTER
Thread(target=KafkaService().consumer, args=(main_app, os.getenv("TOPIC_SERVICES_REGISTER"), callbacks.service_register,)).start()


if __name__ == '__main__':


    host =  os.getenv("APP_HOST")
    port =  os.getenv("APP_PORT")
    debug =  os.getenv("DEBUG")
    #app.run(host=host, port=port, debug=debug, use_reloader=debug)