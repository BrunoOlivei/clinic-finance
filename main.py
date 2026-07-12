import requests

from src.core.config import settings

payload = {
    "username": settings.communicare_username.get_secret_value(),
    "password": settings.communicare_password.get_secret_value(),
}

response = requests.post(settings.communicare_url_login, json=payload)

print(response.json())