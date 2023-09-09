from src.extensions.flask_sqlalchemy import db
from src import models
from sqlalchemy import cast, String

__module_name__ = 'src.repository_item'


def create(automation, first_step, new_item):
    item = models.Item(**new_item)
    item.automation = automation
    item.step = first_step

    db.session.add(item)
    db.session.commit()

    return item


def get_all_by_automation_step_id(step_id,  search=''):
    return models.Item.query.filter_by(step_id=step_id).filter(
        cast(models.Item.data, String).ilike('%{}%'.format(search))).order_by(models.Item.id).all()


def get_all_by_automation_id(automation_id):
    return models.Item.query.join(
        models.Step).filter(
        models.Step.automation_id == automation_id).order_by(models.Item.id).all()


def get_by_uuid(uuid):
    return models.Item.query.filter_by(uuid=uuid).first()


def update(item, new_item):
    for key, value in new_item.items():
        setattr(item, key, value)

    db.session.commit()

    return item


def update_status(item):
    db.session.commit()
    return item


def delete(item):
    db.session.delete(item)
    db.session.commit()
    return item
