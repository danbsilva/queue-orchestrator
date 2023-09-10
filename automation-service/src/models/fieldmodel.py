from datetime import datetime
from uuid import uuid4

from sqlalchemy import or_

from src.extensions.flask_sqlalchemy import db
from src.models.stepmodel import StepModel

class FieldModel(db.Model):
    __tablename__ = 'fields'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
    step = db.relationship('StepModel', backref=db.backref('fields', lazy=True))
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

    @staticmethod
    def create(step, new_field):
        field = FieldModel(**new_field)
        field.step_id = step.id

        db.session.add(field)
        db.session.commit()

        return field


    @staticmethod
    def get_all(step,  search=''):
        return FieldModel.query.filter_by(step_id=step.id).filter(
            or_(
                FieldModel.name.ilike('%{}%'.format(search)),
                FieldModel.alias.ilike('%{}%'.format(search)),
                FieldModel.description.ilike('%{}%'.format(search))
            )
        ).order_by(FieldModel.id).all()


    @staticmethod
    def get_by_id(id):
        return FieldModel.query.filter_by(id=id).first()


    @staticmethod
    def get_by_uuid(uuid):
        return FieldModel.query.filter_by(uuid=uuid).first()



    @staticmethod
    def get_field_by_step_id(step_id, field):
        return FieldModel.query.filter_by(step_id=step_id, field=field).first()


    @staticmethod
    def update(field, new_field):
        for key, value in new_field.items():
            setattr(field, key, value)

        db.session.commit()

        return field


    @staticmethod
    def delete(field):
        db.session.delete(field)
        db.session.commit()
