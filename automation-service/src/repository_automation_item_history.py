from src.extensions.flask_sqlalchemy import db
from src import models


__module_name__ = 'src.repository_automation_item_history'


def create(automation_item, description):
    history = models.AutomationItemHistory()
    history.automation_item = automation_item
    history.description = description

    db.session.add(history)
    db.session.commit()

    return history


def get_all_by_automation_item_id(automation_item_id):
    return models.AutomationItemHistory.query.filter_by(automation_item_id=automation_item_id).all()
