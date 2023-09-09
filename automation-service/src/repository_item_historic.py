from src.extensions.flask_sqlalchemy import db
from src import models


__module_name__ = 'src.repository_item_history'


def create(item, description):
    history = models.ItemHistoric()
    history.item = item
    history.description = description

    db.session.add(history)
    db.session.commit()

    return history


def get_all_by_item_id(item_id):
    return models.ItemHistoric.query.filter_by(item_id=item_id).all()

def delete(history):
    db.session.delete(history)
    db.session.commit()
    return history
