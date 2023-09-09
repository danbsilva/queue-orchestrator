from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db

class ServiceModel(db.Model):
    __tablename__ = 'services_logs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service_name = db.Column(db.String, nullable=False)
    transaction_id = db.Column(db.String, nullable=True)
    level = db.Column(db.String, nullable=False)
    module_name = db.Column(db.String, nullable=False)
    function_name = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)

    def to_json(self):
        return {
            'uuid': self.uuid,
            'datetime': self.datetime,
            'service_name': self.service_name,
            'transaction_id': self.transaction_id,
            'level': self.level,
            'module_name': self.module_name,
            'function_name': self.function_name,
            'message': self.message,
        }

    @staticmethod
    def save(service_log):
        service_log = ServiceModel(**service_log)
        db.session.add(service_log)
        db.session.commit()
        return service_log

    @staticmethod
    def get_all():
        return ServiceModel.query.all()