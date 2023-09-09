from src.extensions.flask_sqlalchemy import db
from src import models

__module_name__ = 'src.repository_automation_step'


def create(automation, new_automation_step):
    automation_step = models.Step(**new_automation_step)
    automation_step.automation = automation

    db.session.add(automation_step)
    db.session.commit()

    return automation_step


def get_all(automation):
    return models.Step.query.filter_by(automation_id=automation.id).order_by(models.Step.step).all()


def get_by_id(id):
    return models.Step.query.filter_by(id=id).first()

def get_by_uuid(uuid):
    return models.Step.query.filter_by(uuid=uuid).first()


def get_by_topic(topic):
    return models.Step.query.filter_by(topic=topic).first()


def get_by_name(name):
    return models.Step.query.filter_by(name=name).first()


def get_step_by_automation_id(automation_id, step):
    return models.Step.query.filter_by(automation_id=automation_id, step=step).first()


def get_steps_by_automation_id(automation_id):
    return models.Step.query.filter_by(automation_id=automation_id).order_by(models.Step.step).all()


def get_step_by_uuid(uuid):
    return models.Step.query.filter_by(uuid=uuid).first()


def update(automation_step, new_automation_step):
    for key, value in new_automation_step.items():
        setattr(automation_step, key, value)

    db.session.commit()

    return automation_step


def delete(automation_step):
    db.session.delete(automation_step)
    db.session.commit()
