import os
from decouple import config as config_env

from flask import Flask

from src import extensions, middlewares


settings = os.path.join(os.path.dirname(__file__), 'settings.py')

def minimal_app():
    app = Flask(config_env('APP_NAME'))
    app.config.from_pyfile(settings)

    extensions.load(app)

    return app


def create_app():
    app = minimal_app()

    middlewares.load(app)

    return app

