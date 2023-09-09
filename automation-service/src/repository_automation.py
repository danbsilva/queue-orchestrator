import json

from sqlalchemy import text, or_
from src.extensions.flask_sqlalchemy import db
from src import models_

__module_name__ = 'src.repository_automation'


def create(new_automation):
    automation = models_.Automation(**new_automation)

    db.session.add(automation)
    db.session.commit()

    return automation


def get_all( search=''):
    return models_.Automation.query.filter(
        or_(
            models_.Automation.name.ilike('%{}%'.format(search)),
            models_.Automation.acronym.ilike('%{}%'.format(search)),
            models_.Automation.description.ilike('%{}%'.format(search))
        )
    ).order_by(models_.Automation.id).all()


def get_all_per_page(offset, per_page):
    return models_.Automation.query.offset(offset).limit(per_page).order_by(models_.Automation.id).all()


def get_by_id(id):
    return models_.Automation.query.filter_by(id=id).first()


def get_by_uuid(uuid):
    return models_.Automation.query.filter_by(uuid=uuid).first()


def get_by_acronym(acronym):
    return models_.Automation.query.filter_by(acronym=acronym).first()


def get_by_name(name):
    return models_.Automation.query.filter_by(name=name).first()


def get_owners(automation_uuid,  search=''):
    automation = get_by_uuid(automation_uuid)
    owners = automation.owners
    if owners:
        if search:
            owners = [o for o in owners if search.lower() in o["name"].lower() or search.lower() in o["email"].lower()]

    return owners


def get_by_owner(owner_uuid,  search=''):
    return models_.Automation.query.filter(
        or_(
            models_.Automation.name.ilike('%{}%'.format(search)),
            models_.Automation.acronym.ilike('%{}%'.format(search)),
            models_.Automation.description.ilike('%{}%'.format(search))
        ),
        text(f"CAST(owners AS TEXT) LIKE '%{owner_uuid}%'")).order_by(models_.Automation.id).all()


def update(automation, new_automation):
    for key, value in new_automation.items():
        setattr(automation, key, value)

    db.session.commit()

    return automation


def delete(automation):
    db.session.delete(automation)
    db.session.commit()


def add_owners(automation, owner):
    owners_list = automation.owners
    new_owners_list = [o for o in owners_list if o["uuid"] != owner["uuid"]]
    new_owners_list.append(owner)

    automation.owners = new_owners_list
    db.session.commit()

    return automation


def remove_owners(automation, owner):
    owners_list = automation.owners
    new_owners_list = [o for o in owners_list if o["uuid"] != owner["uuid"]]

    automation.owners = new_owners_list
    db.session.commit()

    return automation