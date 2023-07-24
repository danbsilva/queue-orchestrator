from sqlalchemy import text

from src.extensions.flask_sqlalchemy import db
from src import models

__module_name__ = 'src.repository_automation'


def create(new_automation):
    automation = models.Automation(**new_automation)

    db.session.add(automation)
    db.session.commit()

    return automation


def get_all():
    return models.Automation.query.all()


def get_all_per_page(offset, per_page):
    return models.Automation.query.offset(offset).limit(per_page).all()


def get_by_id(id):
    return models.Automation.query.filter_by(id=id).first()


def get_by_uuid(uuid):
    return models.Automation.query.filter_by(uuid=uuid).first()


def get_by_acronym(acronym):
    return models.Automation.query.filter_by(acronym=acronym).first()


def get_by_name(name):
    return models.Automation.query.filter_by(name=name).first()


def get_by_owner(owner_uuid):
    return models.Automation.query.filter(text(f"CAST(owners AS TEXT) LIKE '%{owner_uuid}%'")).all()


def update(automation, new_automation):
    for key, value in new_automation.items():
        setattr(automation, key, value)

    db.session.commit()

    return automation


def delete(automation):
    db.session.delete(automation)
    db.session.commit()
