from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db

class ServiceLogModel(db.Model):
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


    def __init__(self, service_log):
        self.uuid = service_log['uuid']
        self.datetime = service_log['datetime']
        self.service_name = service_log['service_name']
        self.transaction_id = service_log['transaction_id']
        self.level = service_log['level']
        self.module_name = service_log['module_name']
        self.function_name = service_log['function_name']
        self.message = service_log['message']

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

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self

    def get_all():
        return ServiceLogModel.query.all()