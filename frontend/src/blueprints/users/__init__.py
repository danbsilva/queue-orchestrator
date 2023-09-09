from flask import Blueprint

from src.blueprints.auth.controllers.auth_controller import *

bp = Blueprint("users", __name__, template_folder="templates", static_folder="static", static_url_path='/webui/static', url_prefix="/auth/users")


def init_app(app):
    app.register_blueprint(bp)
