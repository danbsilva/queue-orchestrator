from src.extensions.flask_sqlalchemy import db
from src import models

__module_name__ = 'src.repository_automation_item'


def create(automation, first_step, new_item):
    item = models.Automationitem(**new_item)
    item.automation = automation
    item.automation_step = first_step

    db.session.add(item)
    db.session.commit()

    return item


def get_all_by_automation_step_id(automation_step_id):
    return models.Automationitem.query.filter_by(automation_step_id=automation_step_id).all()


def get_all_by_automation_id(automation_id):
    return models.Automationitem.query.join(
        models.Step).filter(
        models.Step.automation_id == automation_id).all()


def get_by_uuid(uuid):
    return models.Automationitem.query.filter_by(uuid=uuid).first()


def update(item, new_item):
    for key, value in new_item.items():
        setattr(item, key, value)

    db.session.commit()

    return item


def update_status(item):
    db.session.commit()
    return item

