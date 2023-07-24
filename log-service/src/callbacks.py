from src import repository_service_log, repository_request_log


def save_service_log(app, key, msg):
    with app.app_context():

        repository_service_log.create(msg)


def save_request_log(app, key, msg):
    with app.app_context():
        repository_request_log.create(msg)
