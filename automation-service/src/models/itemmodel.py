from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
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


class ItemHistoricModel(db.Model):
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