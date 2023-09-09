from src.extensions.flask_sqlalchemy import db
from src import models
from sqlalchemy import text, or_

__module_name__ = 'src.repository_field.py'


def create(step, new_field):
    field = models.Field(**new_field)
    field.step = step

    db.session.add(field)
    db.session.commit()

    return field


def get_all(step,  search=''):
    return models.Field.query.filter_by(step_id=step.id).filter(
        or_(
            models.Field.name.ilike('%{}%'.format(search)),
            models.Field.alias.ilike('%{}%'.format(search)),
            models.Field.description.ilike('%{}%'.format(search))
        ),
        ).order_by(models.Field.id).all()


def get_by_id(id):
    return models.Field.query.filter_by(id=id).first()

def get_by_uuid(uuid):
    return models.Field.query.filter_by(uuid=uuid).first()


def get_by_name(name):
    return models.Step.query.filter_by(name=name).first()


def get_field_by_step_id(step_id, field):
    return models.Field.query.filter_by(step_id=step_id, field=field).first()

def update(field, new_field):
    for key, value in new_field.items():
        setattr(field, key, value)

    db.session.commit()

    return field


def delete(field):
    db.session.delete(field)
    db.session.commit()
