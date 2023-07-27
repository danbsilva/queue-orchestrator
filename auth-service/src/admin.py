from src import repository


def create_admin(app):
    with app.app_context():
        user = repository.get_by_email(email='admin@admin.com')
        if not user:
            user = {
                'username':'admin',
                'email':'admin@admin.com',
                'name':'admin',
                'password':'admin',
                'email_sent':True,
                'email_valid':True,
                'is_admin':True
            }

            repository.create(user)