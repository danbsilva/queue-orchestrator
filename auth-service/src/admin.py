from src import repository
from threading import Thread

from src import kafka
from uuid import uuid4
from src import schemas


def create_admin(app):
    with app.app_context():
        user = repository.get_by_email(email='admin@admin.com')
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

            repository.create(new_user)

