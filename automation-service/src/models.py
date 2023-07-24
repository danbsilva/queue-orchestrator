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
    owners = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    steps = db.relationship('AutomationStep', back_populates='automation')
    items = db.relationship('AutomationItem', back_populates='automation')

    def __repr__(self):
        return f'<Automation {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
        }


class AutomationStep(db.Model):
    __tablename__ = 'automation_steps'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship('Automation', back_populates='steps')
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String, nullable=False, unique=True)
    try_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    items = db.relationship('AutomationItem', back_populates='automation_step')

    def __repr__(self):
        return f'<AutomationStep {self.name}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_id': self.automation_id,
            'name': self.name,
            'description': self.description,
            'step': self.step,
        }


class AutomationItem(db.Model):
    __tablename__ = 'automation_items'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship('Automation', back_populates='items')
    automation_step_id = db.Column(db.Integer, db.ForeignKey('automation_steps.id'), nullable=False)
    automation_step = db.relationship('AutomationStep', back_populates='items')
    data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    history = db.relationship('AutomationItemHistory', back_populates='automation_item')

    def __repr__(self):
        return f'<AutomationItem {self.uuid}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_id': self.automation_id,
            'automation_step_id': self.automation_step_id,
            'data': self.data,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class AutomationItemHistory(db.Model):
    __tablename__ = 'automation_item_history'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_item_id = db.Column(db.Integer, db.ForeignKey('automation_items.id'), nullable=False)
    automation_item = db.relationship('AutomationItem', back_populates='history')
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AutomationItemHistory {self.uuid}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_item_id': self.automation_item_id,
            'description': self.description,
            'created_at': self.created_at
        }
