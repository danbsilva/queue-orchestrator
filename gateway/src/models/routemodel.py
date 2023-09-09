from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db



class RouteModel(db.Model):

    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, nullable=False, default=lambda: str(uuid4()))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
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
    
    @staticmethod
    def create(service, new_route):
        route = RouteModel(**new_route)
        route.service_id = service.id

        db.session.add(route)
        db.session.commit()

        return route


    @staticmethod
    def get_by_uuid(uuid):
        return RouteModel.query.filter_by(uuid=uuid).first()


    @staticmethod
    def get_by_service_id_and_route(service_id, route):
        return RouteModel.query.filter_by(service_id=service_id, route=route).first()



    @staticmethod
    def get_by_service_id(service_id):
        return RouteModel.query.filter_by(service_id=service_id).all()


    @staticmethod
    def get_by_route(route):
        return RouteModel.query.filter_by(route=route).first()


    @staticmethod
    def update(route, new_route):
        for key, value in new_route.items():
            if route.__getattribute__(key) != value:
                setattr(route, key, value)

        db.session.commit()

        return route
