from flask import Blueprint

from src.blueprints.webui.controllers.index_controller import *

bp = Blueprint("webui", __name__, template_folder="templates", static_folder="static", static_url_path='/webui/static', url_prefix="/webui")

bp.add_url_rule("/home", view_func=home, endpoint='home', methods=['GET'])


def init_app(app):
    app.register_blueprint(bp)
