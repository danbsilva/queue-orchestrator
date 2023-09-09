from src.models.servicemodel import ServiceModel
from src.models.requestmodel import RequestModel
from src.services.datadogservice import DataDogService


def save_service(app, key, msg):
    with app.app_context():
        ServiceModel.save(msg)
        DataDogService().submit_log(msg)


def save_request(app, key, msg):
    with app.app_context():
        RequestModel.save(msg)
