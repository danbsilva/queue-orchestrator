from src.extensions.flask_sqlalchemy import db
from src import models


def create(service, new_service_route):
    service_route = models.ServiceRoutes(**new_service_route)
    service_route.service = service

    db.session.add(service_route)
    db.session.commit()

    return service_route

def get_by_uuid(uuid):
    return models.ServiceRoutes.query.filter_by(uuid=uuid).first()

def get_by_service_id_and_route(service_id, route):
    return models.ServiceRoutes.query.filter_by(service_id=service_id, route=route).first()


def get_by_service_id(service_id):
    return models.ServiceRoutes.query.filter_by(service_id=service_id).all()

def get_by_route(route):
    return models.ServiceRoutes.query.filter_by(route=route).first()

def update(service_route, new_service_route):
    for key, value in new_service_route.items():
        if service_route.__getattribute__(key) != value:
            setattr(service_route, key, value)

    db.session.commit()

    return service_route
