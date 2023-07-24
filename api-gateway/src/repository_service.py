from src.extensions.flask_sqlalchemy import db
from src import models


def create(new_service):
    service = models.Service(**new_service)

    db.session.add(service)
    db.session.commit()

    return service


def get_all():
    return models.Service.query.all()


def get_by_service_name(service_name):
    return models.Service.query.filter_by(service_name=service_name).first()


def get_by_uuid(uuid):
    return models.Service.query.filter_by(uuid=uuid).first()


def update(service, new_service):
    for key, value in new_service.items():
        setattr(service, key, value)

    db.session.commit()

    return service


def update_service_status(service, new_service_status):
    setattr(service, 'service_status', new_service_status)

    db.session.commit()

    return service
