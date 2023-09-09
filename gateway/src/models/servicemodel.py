from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class ServiceModel(db.Model):

    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    service_name = db.Column(db.String, nullable=False)
    service_host = db.Column(db.String, nullable=False)
    service_status = db.Column(db.Boolean, nullable=True, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'service_name': self.service_name,
            'service_host': self.service_host,
            'service_status': self.service_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }

    @staticmethod
    def create(new_service):
        service = ServiceModel(**new_service)

        db.session.add(service)
        db.session.commit()

        return service


    @staticmethod
    def get_all():
        return ServiceModel.query.order_by(ServiceModel.service_name).all()


    @staticmethod
    def get_by_service_name(service_name):
        return ServiceModel.query.filter_by(service_name=service_name).first()


    @staticmethod
    def get_by_uuid(uuid):
        return ServiceModel.query.filter_by(uuid=uuid).first()


    @staticmethod
    def get_by_id(id):
        return ServiceModel.query.filter_by(id=id).first()


    @staticmethod
    def update(service, new_service):
        for key, value in new_service.items():
            setattr(service, key, value)

        db.session.commit()

        return service


    @staticmethod
    def update_service_status(service, new_service_status):
        setattr(service, 'service_status', new_service_status)

        db.session.commit()

        return service
    