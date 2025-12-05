import requests
from django.conf import settings
from sms.eskiz_client import get_token, refresh_token

BASE_URL = "https://notify.eskiz.uz/api"


def send_sms(phone: str, message: str, user_sms_id=None, sender=None):
    token = get_token()
    url = f"{BASE_URL}/message/sms/send"

    payload = {
        "mobile_phone": phone,
        "message": message,
        "from": sender or getattr(settings, "ESKIZ_FROM", "")
    }

    if user_sms_id:
        payload["user_sms_id"] = user_sms_id

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.post(url, data=payload, headers=headers)

    if r.status_code == 401:
        token = refresh_token()
        headers["Authorization"] = f"Bearer {token}"
        r = requests.post(url, data=payload, headers=headers)

    return r.json()
