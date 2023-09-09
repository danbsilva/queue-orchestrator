from os import path
from decouple import config as config_env

BASE_DIR = path.dirname(path.realpath(__file__))

# APP
DEBUG = config_env('DEBUG')
FLASK_ENV = config_env('FLASK_ENV')
FLASK_APP = config_env('FLASK_APP')
APP_PORT = int(config_env('APP_PORT'))
APP_HOST = config_env('APP_HOST')
CONTAINER_NAME = config_env('CONTAINER_NAME')

# KEYS
ALGORITHM = config_env('ALGORITHM')
SECRET_KEY = config_env('SECRET_KEY')

# REDIS
CACHE_TYPE = config_env('CACHE_TYPE')
CACHE_REDIS_HOST = config_env('CACHE_REDIS_HOST')
CACHE_REDIS_PORT = config_env('CACHE_REDIS_PORT')
CACHE_REDIS_DB = config_env('CACHE_REDIS_DB')
CACHE_REDIS_URL = config_env('CACHE_REDIS_URL')
CACHE_DEFAULT_TIMEOUT = config_env('CACHE_DEFAULT_TIMEOUT')

# KAFA
KAFKA_SERVER = config_env('KAFKA_SERVER')

# EXTENSIONS
EXTENSIONS = [
    'src.blueprints.auth:init_app',
    'src.blueprints.users:init_app',
    'src.blueprints.automations:init_app',
    'src.blueprints.webui:init_app',
    'src.extensions.flask_cache:init_app',
    'src.extensions.flask_jsglue:init_app',
    'src.extensions.flask_csrf:init_app',

]
