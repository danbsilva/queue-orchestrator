from flask import Blueprint

from src.blueprints.automations.controllers.automations_controller import *

bp = Blueprint("automations", __name__, template_folder="templates", static_folder="static", static_url_path='/webui/static', url_prefix="/automations")


# AUTOMATIONS
bp.add_url_rule("/", view_func=automations, endpoint='automations', methods=['GET'])
bp.add_url_rule("/page_automations/", view_func=page_automations, endpoint='page_automations', methods=['GET'])
bp.add_url_rule("/new/", view_func=new_automation, endpoint='new_automation', methods=['GET', 'POST'])
bp.add_url_rule("/<uuid>/edit/", view_func=edit_automation, endpoint='edit_automation', methods=['GET', 'POST'])
bp.add_url_rule("/<uuid>/view/", view_func=view_automation, endpoint='view_automation', methods=['GET'])
bp.add_url_rule("/<uuid>/detail/", view_func=detail_automation, endpoint='detail_automation', methods=['GET'])
bp.add_url_rule("/<uuid>/delete/", view_func=delete_automation, endpoint='delete_automation', methods=['GET', 'POST'])

# OWNERS
bp.add_url_rule("/<automation_uuid>/page_owners/", view_func=page_owners, endpoint='page_owners', methods=['GET'])
bp.add_url_rule("/<automation_uuid>/owners/new/", view_func=new_owner, endpoint='new_owner', methods=['GET', 'POST'])
bp.add_url_rule("/<automation_uuid>/owners/delete/", view_func=delete_owners, endpoint='delete_owners', methods=['GET', 'POST'])

# STEPS
bp.add_url_rule("/<automation_uuid>/steps/", view_func=steps, endpoint='steps', methods=['GET'])
bp.add_url_rule("/<automation_uuid>/page_steps/", view_func=page_steps, endpoint='page_steps', methods=['GET'])
bp.add_url_rule("/<automation_uuid>/steps/new/", view_func=new_step, endpoint='new_step', methods=['GET', 'POST'])
bp.add_url_rule("/<automation_uuid>/steps/<uuid>/edit/", view_func=edit_step, endpoint='edit_step', methods=['GET', 'POST'])
bp.add_url_rule("/steps/<uuid>/view/", view_func=view_step, endpoint='view_step', methods=['GET'])
bp.add_url_rule("/steps/<uuid>/detail/", view_func=detail_step, endpoint='detail_step', methods=['GET'])
bp.add_url_rule("/steps/<uuid>/delete/", view_func=delete_step, endpoint='delete_step', methods=['GET', 'POST'])

# FIELDS
bp.add_url_rule("/stpes/<step_uuid>/page_fields/", view_func=page_fields, endpoint='page_fields', methods=['GET'])
bp.add_url_rule("/steps/<step_uuid>/fields/new/", view_func=new_field, endpoint='new_field', methods=['GET', 'POST'])
bp.add_url_rule("/steps/fields/<uuid>/edit/", view_func=edit_field, endpoint='edit_field', methods=['GET', 'POST'])
bp.add_url_rule("/steps/fields/<uuid>/delete/", view_func=delete_field, endpoint='delete_field', methods=['GET', 'POST'])

# ITEMS
bp.add_url_rule("/<automation_uuid>/items/", view_func=items_by_automation, endpoint='items_by_automation', methods=['GET'])
bp.add_url_rule("/<automation_uuid>/page_items_by_automation/", view_func=page_items_by_automation, endpoint='page_items_by_automation', methods=['GET'])
bp.add_url_rule("/steps/<step_uuid>/page_items/", view_func=page_items, endpoint='page_items', methods=['GET'])
bp.add_url_rule("/steps/<step_uuid>/items/new/", view_func=new_item, endpoint='new_item', methods=['GET', 'POST'])
bp.add_url_rule("/steps/items/<uuid>/edit/", view_func=edit_item, endpoint='edit_item', methods=['GET', 'POST'])
bp.add_url_rule("/steps/items/<uuid>/view/", view_func=view_item, endpoint='view_item', methods=['GET'])
bp.add_url_rule("/steps/items/<uuid>/detail/", view_func=detail_item, endpoint='detail_item', methods=['GET'])
bp.add_url_rule("/steps/items/<uuid>/delete/", view_func=delete_item, endpoint='delete_item', methods=['GET', 'POST'])


# HISTORIC
bp.add_url_rule("/steps/items/<item_uuid>/page_historic/", view_func=page_historic, endpoint='page_historic', methods=['GET'])

def init_app(app):
    app.register_blueprint(bp)
