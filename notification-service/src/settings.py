from os import path
from decouple import config as config_env

BASE_DIR = path.dirname(path.realpath(__file__))

# APP
DEBUG = eval(config_env('DEBUG').title())
FLASK_ENV = config_env('FLASK_ENV')
FLASK_APP = config_env('FLASK_APP')
APP_PORT = int(config_env('APP_PORT'))
APP_HOST = config_env('APP_HOST')
CONTAINER_NAME = config_env('CONTAINER_NAME')

# API GATEWAY
API_GATEWAY_HOST = config_env('API_GATEWAY_HOST')

# MAIL
MAIL_SERVER = config_env('MAIL_SERVER')
MAIL_PORT = config_env('MAIL_PORT')
MAIL_USE_TLS = config_env('MAIL_USE_TLS')
MAIL_USERNAME = config_env('MAIL_USERNAME')
MAIL_PASSWORD = config_env('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = config_env('MAIL_DEFAULT_SENDER')

# KAFKA
KAFKA_SERVER = config_env('KAFKA_SERVER')

EXTENSIONS = [
    'src.extensions.mail:init_app'
]
