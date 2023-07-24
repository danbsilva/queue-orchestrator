from os import path
from decouple import config as config_env

BASE_DIR = path.dirname(path.realpath(__file__))

# APP
DEBUG = config_env('DEBUG')
FLASK_ENV = config_env('FLASK_ENV')
FLASK_APP = config_env('FLASK_APP')
APP_NAME = config_env('APP_NAME')
APP_PORT = int(config_env('APP_PORT'))
APP_HOST = config_env('APP_HOST')
CONTAINER_NAME = config_env('CONTAINER_NAME')

# API GATEWAY
API_GATEWAY_HOST = config_env('API_GATEWAY_HOST')

# KEYS
ALGORITHM = config_env('ALGORITHM')
SECRET_KEY = config_env('SECRET_KEY')

# DB
SQLALCHEMY_DATABASE_URI = config_env('SQLALCHEMY_DATABASE_URI')
BUNDLE_ERRORS = config_env('BUNDLE_ERRORS')

# REDIS
CACHE_TYPE = config_env('CACHE_TYPE')
CACHE_REDIS_HOST = config_env('CACHE_REDIS_HOST')
CACHE_REDIS_PORT = config_env('CACHE_REDIS_PORT')
CACHE_REDIS_DB = config_env('CACHE_REDIS_DB')
CACHE_REDIS_URL = config_env('CACHE_REDIS_URL')
CACHE_DEFAULT_TIMEOUT = config_env('CACHE_DEFAULT_TIMEOUT')

# KAFKA
KAFKA_SERVER = config_env('KAFKA_SERVER')

# TOPICS
TOPIC_SEND_EMAIL_VALIDATION = config_env('TOPIC_SEND_EMAIL_VALIDATION')

EXTENSIONS = [
    'src.routes:init_app',
    'src.extensions.flask_sqlalchemy:init_app',
    'src.extensions.flask_marshmallow:init_app',
    'src.extensions.flask_cache:init_app',
]
