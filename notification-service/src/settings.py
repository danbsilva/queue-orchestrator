import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# APP
DEBUG = int(os.getenv("DEBUG"))
FLASK_ENV = os.getenv("FLASK_ENV")
FLASK_APP = os.getenv("FLASK_APP")
APP_NAME = os.getenv('APP_NAME')
APP_PORT = int(os.getenv('APP_PORT'))
APP_HOST = os.getenv('APP_HOST')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')


# MAIL
MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')


EXTENSIONS = [
    'src.extensions.mail:init_app'
]
