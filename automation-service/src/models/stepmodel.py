from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class StepModel(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    step = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String, nullable=False, unique=True)
    try_count = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
