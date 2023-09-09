from src.extensions.flask_sqlalchemy import db
from src import models


__module_name__ = 'src.repository_item_historic'


def create(item, description):
    historic = models.ItemHistoric()
    historic.item = item
    historic.description = description

    db.session.add(historic)
    db.session.commit()

    return historic


def get_all_by_item_id(item_id):
    return models.ItemHistoric.query.filter_by(item_id=item_id).order_by(models.ItemHistoric.id).all()

def delete(historic):
    db.session.delete(historic)
    db.session.commit()
    return historic
