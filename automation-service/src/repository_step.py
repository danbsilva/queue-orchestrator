from src.extensions.flask_sqlalchemy import db
from src import models
from sqlalchemy import text, or_

__module_name__ = 'src.repository_step'


def create(automation, new_step):
    step = models.Step(**new_step)
    step.automation = automation

    db.session.add(step)
    db.session.commit()

    return step


def get_all(automation_id, search=''):
    return models.Step.query.filter_by(automation_id=automation_id).filter(
        or_(
            models.Step.name.ilike('%{}%'.format(search)),
            models.Step.description.ilike('%{}%'.format(search))
        )
    ).order_by(models.Step.step).all()


def get_by_id(id):
    return models.Step.query.filter_by(id=id).first()


def get_by_uuid(uuid):
    return models.Step.query.filter_by(uuid=uuid).first()


def get_by_topic(topic):
    return models.Step.query.filter_by(topic=topic).first()


def get_by_name(name):
    return models.Step.query.filter_by(name=name).first()


def get_by_name_and_automation_id(automation_id, name):
    return models.Step.query.filter_by(automation_id=automation_id, name=name).first()


def get_step_by_automation_id(automation_id, step):
    return models.Step.query.filter_by(automation_id=automation_id, step=step).first()


def get_steps_by_automation_id(automation_id):
    return models.Step.query.filter_by(automation_id=automation_id).order_by(models.Step.step).all()


def get_step_by_uuid(uuid):
    return models.Step.query.filter_by(uuid=uuid).first()


def update(step, new_step):
    for key, value in new_step.items():
        setattr(step, key, value)

    db.session.commit()

    return step


def delete(step):
    db.session.delete(step)
    db.session.commit()
