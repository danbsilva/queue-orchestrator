import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# APP
DEBUG = os.getenv("DEBUG")
FLASK_ENV = os.getenv("FLASK_ENV")
FLASK_APP = os.getenv("FLASK_APP")
APP_NAME = os.getenv("APP_NAME")
APP_PORT = int(os.getenv("APP_PORT"))
APP_HOST = os.getenv("APP_HOST")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")


# DB
BUNDLE_ERRORS = os.getenv("BUNDLE_ERRORS")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


# REDIS
CACHE_TYPE = os.getenv("CACHE_TYPE")
CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST")
CACHE_REDIS_PORT = os.getenv("CACHE_REDIS_PORT")
CACHE_REDIS_DB = os.getenv("CACHE_REDIS_DB")
CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")
CACHE_DEFAULT_TIMEOUT = os.getenv("CACHE_DEFAULT_TIMEOUT")


# EXTENSIONS
EXTENSIONS = [
    'src.routes:init_app',
    'src.extensions.flask_sqlalchemy:init_app',
    'src.extensions.flask_marshmallow:init_app',
    'src.extensions.flask_cache:init_app',

]
