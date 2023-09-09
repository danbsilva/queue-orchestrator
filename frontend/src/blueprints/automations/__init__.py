from flask import Blueprint

from src.blueprints.auth.controllers.auth_controller import *

bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static", static_url_path='/webui/static', url_prefix="/auth")

bp.add_url_rule("/login", view_func=login, endpoint='login', methods=['GET', 'POST'])
bp.add_url_rule("/logout", view_func=logout, endpoint='logout', methods=['GET', 'POST'])


def init_app(app):
    app.register_blueprint(bp)
