from src.extensions.flask_sqlalchemy import db
from src import models


def create(new_request_log):
    request_log = models.RequestLog(**new_request_log)
    db.session.add(request_log)
    db.session.commit()
    return request_log


def get_all():
    return models.RequestLog.query.all()
