from datetime import datetime
from uuid import uuid4

from sqlalchemy import or_

from src.extensions.flask_sqlalchemy import db

from src.models.automationmodel import AutomationModel


class StepModel(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship('AutomationModel', backref=db.backref('steps', lazy=True))
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

    @staticmethod
    def create(automation, new_step):
        step = StepModel(**new_step)
        step.automation_id = automation.id

        db.session.add(step)
        db.session.commit()

        return step


    @staticmethod
    def get_all(automation_id, search=''):
        return StepModel.query.filter_by(automation_id=automation_id).filter(
            or_(
                StepModel.name.ilike('%{}%'.format(search)),
                StepModel.description.ilike('%{}%'.format(search))
            )
        ).order_by(StepModel.step).all()


    @staticmethod
    def get_by_id(id):
        return StepModel.query.filter_by(id=id).first()


    @staticmethod
    def get_by_uuid(uuid):
        return StepModel.query.filter_by(uuid=uuid).first()


    @staticmethod
    def get_by_topic(topic):
        return StepModel.query.filter_by(topic=topic).first()


    @staticmethod
    def get_by_name(name):
        return StepModel.query.filter_by(name=name).first()


    @staticmethod
    def get_by_name_and_automation_id(automation_id, name):
        return StepModel.query.filter_by(automation_id=automation_id, name=name).first()


    @staticmethod
    def get_step_by_automation_id(automation_id, step):
        return StepModel.query.filter_by(automation_id=automation_id, step=step).first()


    @staticmethod
    def get_steps_by_automation_id(automation_id):
        return StepModel.query.filter_by(automation_id=automation_id).order_by(StepModel.step).all()


    @staticmethod
    def get_step_by_uuid(uuid):
        return StepModel.query.filter_by(uuid=uuid).first()


    @staticmethod
    def update(step, new_step):
        for key, value in new_step.items():
            setattr(step, key, value)

        db.session.commit()

        return step


    @staticmethod
    def delete(step):
        db.session.delete(step)
        db.session.commit()