import os

from flask import Flask

from src import admin
from src import extensions, middlewares


settings = os.path.join(os.path.dirname(__file__), 'settings.py')

def minimal_app():
    app = Flask(os.getenv('APP_NAME'))
    app.config.from_pyfile(settings)

    # Load extensions
    extensions.load(app=app)

    return app


def create_app():
    app = minimal_app()

    # Load middlewares
    middlewares.load(app=app)

    # Create admin user
    admin.create_admin(app=app)

    return app
