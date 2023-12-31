from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    Migrate(app=app, db=db)
    app.db = db
    with app.app_context():
        db.create_all()