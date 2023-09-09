from src.models.usermodel import UserModel
from threading import Thread

from src.services.kafkaservice import KafkaService
from uuid import uuid4
from src.schemas import userschemas


def create_admin(app):
    with app.app_context():
        user = UserModel.get_by_email(email='admin@admin.com')
        if not user:
            new_user = {
                'username':'admin',
                'email':'admin@admin.com',
                'name':'admin',
                'password':'admin',
                'email_sent':True,
                'email_valid':True,
                'is_admin':True
            }

            UserModel.save(new_user)

