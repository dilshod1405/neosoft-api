import requests
from django.conf import settings

def multicard_get_token():
    url = f"{settings.MULTICARD_API_URL.rstrip('/')}/auth"
    payload = {
        "application_id": settings.MULTICARD_APP_ID,
        "secret": settings.MULTICARD_API_KEY,
    }

    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["token"]
