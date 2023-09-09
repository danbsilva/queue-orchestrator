from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class Automation(db.Model):
    __tablename__ = 'automations'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    name = db.Column(db.String, nullable=False)
    acronym = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    owners = db.Column(db.JSON, nullable=True, default=[])
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    steps = db.relationship('Step', back_populates='automation')
    items = db.relationship('Item', back_populates='automation')

    def __repr__(self):
        return f'<Automation {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
            'owners': self.owners
        }


class Step(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship('Automation', back_populates='steps')
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String, nullable=False, unique=True)
    try_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('Item', back_populates='step')
    fields = db.relationship('Field', back_populates='step')

    def __repr__(self):
        return f'<Step {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_id': self.automation_id,
            'name': self.name,
            'description': self.description,
            'step': self.step,
            'topic': self.topic,
            'try_count': self.try_count
        }


class Field(db.Model):
    __tablename__ = 'fields'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
    step = db.relationship('Step', back_populates='fields')
    name = db.Column(db.String, nullable=False)
    alias = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    required = db.Column(db.Boolean, nullable=False, default=True)
    default = db.Column(db.String, nullable=True)
    options = db.Column(db.JSON, nullable=True, default=[])
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Field {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'step_id': self.step_id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'required': self.required,
            'default': self.default,
            'options': self.options
        }


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship('Automation', back_populates='items')
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
    step = db.relationship('Step', back_populates='items')
    data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    historic = db.relationship('ItemHistoric', back_populates='item')

    def __repr__(self):
        return f'<Item {self.uuid}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_id': self.automation_id,
            'step_id': self.step_id,
            'data': self.data,
            'status': self.status
        }


class ItemHistoric(db.Model):
    __tablename__ = 'item_historic'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    item = db.relationship('Item', back_populates='historic')
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ItemHistoric {self.uuid}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'item_id': self.item_id,
            'description': self.description,
            'created_at': self.created_at
        }