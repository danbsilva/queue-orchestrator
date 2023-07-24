from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class ServiceLog(db.Model):
    __tablename__ = 'services_logs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service_name = db.Column(db.String, nullable=False)
    transaction_id = db.Column(db.String, nullable=False)
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


class RequestLog(db.Model):
    __tablename__ = 'requests_logs'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service = db.Column(db.String, nullable=False)
    transaction_id = db.Column(db.String, nullable=False)
    ip = db.Column(db.String, nullable=False)
    method = db.Column(db.String, nullable=False)
    endpoint = db.Column(db.String, nullable=False)
    params = db.Column(db.String, nullable=True)
    status = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Float, nullable=False)

    def to_json(self):
        return {
            'uuid': self.uuid,
            'datetime': self.datetime,
            'service': self.service,
            'transaction_id': self.transaction_id,
            'ip': self.ip,
            'method': self.method,
            'endpoint': self.endpoint,
            'params': self.params,
            'status': self.status,
            'duration': self.duration,
        }
