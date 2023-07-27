from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db


class Service(db.Model):

    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    service_name = db.Column(db.String, nullable=False)
    service_host = db.Column(db.String, nullable=False)
    service_status = db.Column(db.Boolean, nullable=True, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service_routes = db.relationship('ServiceRoutes', back_populates='service')

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


class ServiceRoutes(db.Model):

    __tablename__ = 'service_routes'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    service = db.relationship('Service', back_populates='service_routes')
    route = db.Column(db.String, nullable=False)
    args = db.Column(db.String, nullable=True)
    methods_allowed = db.Column(db.JSON, nullable=False)
    required_auth = db.Column(db.Boolean, nullable=False, default=True)
    required_admin = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_json(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'service_id': self.service_id,
            'route': self.route,
            'args': self.args,
            'methods_allowed': self.methods_allowed,
            'required_auth': self.required_auth,
            'required_admin': self.required_admin,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }