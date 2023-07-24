from src.extensions.flask_sqlalchemy import db
from src import models


def create(service, new_service_route):
    service_route = models.ServiceRoutes(**new_service_route)
    service_route.service = service

    db.session.add(service_route)
    db.session.commit()

    return service_route


def get_by_service_id_and_route(service_id, route):
    return models.ServiceRoutes.query.filter_by(service_id=service_id, route=route).first()


def get_by_service_id(service_id):
    return models.ServiceRoutes.query.filter_by(service_id=service_id).all()


def update(service_route, new_service_route):
    for key, value in new_service_route.items():
        setattr(service_route, key, value)

    db.session.commit()

    return service_route
