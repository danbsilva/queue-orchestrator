from datetime import datetime
from uuid import uuid4

from src.extensions.flask_sqlalchemy import db
from src.providers.hash_provider import generate_password_hash


class User(db.Model):

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

    def generate_uuid(self):
        self.uuid = uuid4().hex

    def generate_username(self):
        self.username = self.uuid

    def encode_password(self):
        self.password = generate_password_hash(self.password)

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
