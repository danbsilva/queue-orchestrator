from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class FieldModel(db.Model):
    __tablename__ = 'fields'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
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
