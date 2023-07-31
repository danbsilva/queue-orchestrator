from src.extensions.flask_sqlalchemy import db
from src import models


def create(service, new_service_documentation):
    service_documentantion = models.ServiceDocumentations(**new_service_documentation)
    service_documentantion.service = service

    db.session.add(service_documentantion)
    db.session.commit()

    return service_documentantion

def get_by_uuid(uuid):
    return models.ServiceDocumentations.query.filter_by(uuid=uuid).first()


def get_by_service_id(service_id):
    return models.ServiceDocumentations.query.filter_by(service_id=service_id).first()


def update(service_documentation, new_service_documentation):
    for key, value in new_service_documentation.items():
        setattr(service_documentation, key, value)

    db.session.commit()

    return service_documentation
