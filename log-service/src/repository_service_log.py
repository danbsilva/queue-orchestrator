from src.extensions.flask_sqlalchemy import db
from src import models


def create(new_service_log):
    log = models.ServiceLog(**new_service_log)
    db.session.add(log)
    db.session.commit()
    return log


def get_all():
    return models.ServiceLog.query.all()
