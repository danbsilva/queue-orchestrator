from src.extensions.flask_sqlalchemy import db
from src import models

__module_name__ = 'src.repository'


def create(new_user):
    user = models.User(**new_user)

    user.generate_uuid()
    user.generate_username()
    user.encode_password()

    db.session.add(user)
    db.session.commit()

    return user


def get_all():
    return models.User.query.all()


def get_by_email(email):
    return models.User.query.filter_by(email=email).first()


def get_by_uuid(uuid):
    return models.User.query.filter_by(uuid=uuid).first()


def get_by_username(username):
    return models.User.query.filter_by(username=username).first()


def update(user, data):
    for key, value in data.items():
        setattr(user, key, value)
    db.session.commit()

    return user


def delete(user):
    db.session.delete(user)
    db.session.commit()


def change_password(user, new_password):
    user.password = new_password
    user.encode_password()
    db.session.commit()

    return user


def validate_email(user):
    user.email_valid = True
    db.session.commit()

    return user

def update_role(user):
    if user.is_admin:
        user.is_admin = False
    else:
        user.is_admin = True

    db.session.commit()

    return user
