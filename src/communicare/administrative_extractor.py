import requests
from src.core.config import settings

class AdministrativeReport:
    def __init__(self):
        self.clinic = "1274,0"
        self.professional = "262586,0"

    def login(self) -> str:
        payload = {
            "username": settings.communicare_username.get_secret_value(),
            "password": settings.communicare_password.get_secret_value(),
        }
        response = requests.post(settings.communicare_url_login, json=payload)
        token = response.json()["token"]
        return token

    def administrative_report(self, token: str) -> str:
        url = "https://api-report-production.communicare.com.br/v1/administrative-report/specific"
