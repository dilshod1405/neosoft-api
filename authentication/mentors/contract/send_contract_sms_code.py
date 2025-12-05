import random
from utils.get_redis import get_redis
from sms.sms_sender import send_sms


def generate_sms_code():
    return str(random.randint(100000, 999999))


def send_contract_sms(mentor_id: int, phone: str):
    code = generate_sms_code()
    redis_key = f"sms_code:{phone}"
    get_redis().set(redis_key, code, ex=120)
    print(code)
    message = f"{code}"

    return send_sms(phone, message=message, user_sms_id=mentor_id)