import schedule
import time
import requests
from src import repository_service


def check_microservice_availability(service_url):
    try:
        response = requests.get(f"{service_url}")  # Rota de verificação de saúde do microserviço
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False


def job():
    services = repository_service.get_all()
    for service in services:
        if check_microservice_availability(f'{service.service_host}/health/'):
            service.service_status = True
            repository_service.update_service_status(service, True)
        else:
            service.service_status = False
            repository_service.update_service_status(service, False)


schedule.every(1).minutes.do(job)


def run_scheduler(app):
    with app.app_context():
        while True:
            schedule.run_pending()
            time.sleep(1)
