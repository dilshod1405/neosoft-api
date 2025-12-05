import requests
from django.conf import settings
from utils.get_redis import get_redis

BASE_URL = "https://notify.eskiz.uz/api"


def save_token(token):
    get_redis().set("eskiz_token", token, ex=3500)
    return token


def load_token():
    return get_redis().get("eskiz_token")


def eskiz_login():
    url = f"{BASE_URL}/auth/login"
    payload = {
        "email": settings.ESKIZ_EMAIL,
        "password": settings.ESKIZ_PASSWORD
    }
    r = requests.post(url, data=payload)
    data = r.json()
    if "data" in data and "token" in data["data"]:
        return save_token(data["data"]["token"])
    return None


def refresh_token():
    token = load_token()
    url = f"{BASE_URL}/auth/refresh"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.patch(url, headers=headers)
    data = r.json()
    if "data" in data and "token" in data["data"]:
        return save_token(data["data"]["token"])
    return eskiz_login()


def get_token():
    token = load_token()
    if token:
        return token
    return eskiz_login()
