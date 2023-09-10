import os
from decouple import config as config_env

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# APP
DEBUG = os.getenv('DEBUG')
FLASK_ENV = os.getenv('FLASK_ENV')
FLASK_APP = os.getenv('FLASK_APP')
APP_NAME = os.getenv('APP_NAME')
APP_PORT = int(os.getenv('APP_PORT'))
APP_HOST = os.getenv('APP_HOST')
CONTAINER_NAME = os.getenv('CONTAINER_NAME')


SECRET_KEY = os.getenv('SECRET_KEY')

# REDIS
CACHE_TYPE = os.getenv('CACHE_TYPE')
CACHE_REDIS_HOST = os.getenv('CACHE_REDIS_HOST')
CACHE_REDIS_PORT = os.getenv('CACHE_REDIS_PORT')
CACHE_REDIS_DB = os.getenv('CACHE_REDIS_DB')
CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL')
CACHE_DEFAULT_TIMEOUT = os.getenv('CACHE_DEFAULT_TIMEOUT')


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
