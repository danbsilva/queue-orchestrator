from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db
from src.providers.hash_provider import generate_password_hash


class UserModel(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True, nullable=False, index=True)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    email = db.Column(db.String, unique=True, nullable=False, index=True)
    name = db.Column(db.String, unique=False, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)
    email_sent = db.Column(db.Boolean, default=False)
    email_valid = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.name

    def to_json(self):
        return {
            'uuid': self.uuid,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'email_sent': self.email_sent,
            'email_valid': self.email_valid,
            'is_admin': self.is_admin
        }


    def generate_uuid(self):
        self.uuid = str(uuid4())

    def generate_username(self):
        self.username = self.uuid

    def encode_password(self):
        self.password = generate_password_hash(self.password)


    @staticmethod
    def save(new_user):
        user = UserModel(**new_user)

        user.generate_uuid()
        user.generate_username()
        user.encode_password()

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def get_all():
        return UserModel.query.all()

    @staticmethod
    def get_by_email(email):
        return UserModel.query.filter_by(email=email).first()

    @staticmethod
    def get_by_uuid(uuid):
        return UserModel.query.filter_by(uuid=uuid).first()

    @staticmethod
    def get_by_username(username):
        return UserModel.query.filter_by(username=username).first()

    @staticmethod
    def update(user, data):
        for key, value in data.items():
            setattr(user, key, value)
        db.session.commit()

        return user

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def change_password(user, new_password):
        user.password = new_password
        user.encode_password()
        db.session.commit()

        return user

    @staticmethod
    def validate_email(user):
        user.email_valid = True
        db.session.commit()

        return user

    @staticmethod
    def change_role(user):
        if user.is_admin:
            user.is_admin = False
        else:
            user.is_admin = True

        db.session.commit()

        return user