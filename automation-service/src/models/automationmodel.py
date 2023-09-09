from datetime import datetime
from uuid import uuid4
from sqlalchemy import text, or_
from src.extensions.flask_sqlalchemy import db


class AutomationModel(db.Model):

    __tablename__ = 'automations'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    name = db.Column(db.String, nullable=False)
    acronym = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    owners = db.Column(db.JSON, nullable=True, default=[])
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AutomationModel {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
            'owners': self.owners
        }

    @staticmethod
    def create(new_automation):
        automation = AutomationModel(**new_automation)

        db.session.add(automation)
        db.session.commit()

        return automation

    @staticmethod
    def get_all(search=''):
        return AutomationModel.query.filter(
            or_(
                AutomationModel.name.ilike('%{}%'.format(search)),
                AutomationModel.acronym.ilike('%{}%'.format(search)),
                AutomationModel.description.ilike('%{}%'.format(search))
            )
        ).order_by(AutomationModel.id).all()

    @staticmethod
    def get_all_per_page(offset, per_page):
        return AutomationModel.query.offset(offset).limit(per_page).order_by(AutomationModel.id).all()

    @staticmethod
    def get_by_id(id):
        return AutomationModel.query.filter_by(id=id).first()

    @staticmethod
    def get_by_uuid(uuid):
        return AutomationModel.query.filter_by(uuid=uuid).first()

    @staticmethod
    def get_by_acronym(acronym):
        return AutomationModel.query.filter_by(acronym=acronym).first()

    @staticmethod
    def get_by_name(name):
        return AutomationModel.query.filter_by(name=name).first()

    @staticmethod
    def get_owners(automation_uuid, search=''):
        automation = AutomationModel.get_by_uuid(automation_uuid)
        owners = automation.owners
        if owners:
            if search:
                owners = [o for o in owners if
                          search.lower() in o["name"].lower() or search.lower() in o["email"].lower()]

        return owners

    @staticmethod
    def get_by_owner(owner_uuid, search=''):
        return AutomationModel.query.filter(
            or_(
                AutomationModel.name.ilike('%{}%'.format(search)),
                AutomationModel.acronym.ilike('%{}%'.format(search)),
                AutomationModel.description.ilike('%{}%'.format(search))
            ),
            text(f"CAST(owners AS TEXT) LIKE '%{owner_uuid}%'")).order_by(AutomationModel.id).all()

    @staticmethod
    def update(automation, new_automation):
        for key, value in new_automation.items():
            setattr(AutomationModel, key, value)

        db.session.commit()

        return automation

    @staticmethod
    def delete(automation):
        db.session.delete(automation)
        db.session.commit()

    @staticmethod
    def add_owners(automation, owner):
        owners_list = automation.owners
        new_owners_list = [o for o in owners_list if o["uuid"] != owner["uuid"]]
        new_owners_list.append(owner)

        automation.owners = new_owners_list
        db.session.commit()

        return AutomationModel

    @staticmethod
    def remove_owners(automation, owner):
        owners_list = automation.owners
        new_owners_list = [o for o in owners_list if o["uuid"] != owner["uuid"]]

        automation.owners = new_owners_list
        db.session.commit()

        return automation