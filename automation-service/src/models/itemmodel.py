from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db
from sqlalchemy import cast, String, or_
from src.models.automationmodel import AutomationModel
from src.models.stepmodel import StepModel


class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    automation_id = db.Column(db.Integer, db.ForeignKey('automations.id'), nullable=False)
    automation = db.relationship(AutomationModel, backref='items', lazy=True)
    step_id = db.Column(db.Integer, db.ForeignKey('steps.id'), nullable=False)
    step = db.relationship(StepModel, backref='items', lazy=True)
    data = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String, nullable=False, default='pending')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ItemModel {self.uuid}>'

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'automation_id': self.automation_id,
            'step_id': self.step_id,
            'data': self.data,
            'status': self.status
        }
    
    @staticmethod
    def create(automation, first_step, new_item):
        item = ItemModel(**new_item)
        item.automation_id = automation.id
        item.step_id = first_step.id

        db.session.add(item)
        db.session.commit()

        return item


    @staticmethod
    def get_all_by_automation_step_id(step_id,  search=''):
        return ItemModel.query.filter_by(step_id=step_id).filter(
            or_(
                cast(ItemModel.data, String).ilike('%{}%'.format(search))
            )
        ).order_by(ItemModel.id).all()


    @staticmethod
    def get_all_by_automation_id(automation_id):
        return ItemModel.query.join(
            StepModel).filter(
            StepModel.automation_id == automation_id).order_by(ItemModel.id).all()


    @staticmethod
    def get_by_uuid(uuid):
        return ItemModel.query.filter_by(uuid=uuid).first()


    @staticmethod
    def update(item, new_item):
        for key, value in new_item.items():
            setattr(item, key, value)

        db.session.commit()

        return item


    @staticmethod
    def update_status(item):
        db.session.commit()
        return item


    @staticmethod
    def delete(item):
        db.session.delete(item)
        db.session.commit()
        return item


class ItemHistoricModel(db.Model):
    __tablename__ = 'item_historic'

    id = db.Column(db.Integer, primary_key=True, index=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
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
    
    @staticmethod
    def create(item, description):
        historic = ItemHistoricModel()
        historic.item_id = item.id
        historic.description = description

        db.session.add(historic)
        db.session.commit()

        return historic


    @staticmethod
    def get_all_by_item_id(item_id):
        return ItemHistoricModel.query.filter_by(item_id=item_id).order_by(ItemHistoricModel.id).all()


    @staticmethod
    def delete(historic):
        db.session.delete(historic)
        db.session.commit()
        return historic