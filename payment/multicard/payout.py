import requests
from django.conf import settings
from payment.mentors.models import MentorBalanceHistory, MentorBalance
from .get_token import multicard_get_token


API_URL = settings.MULTICARD_API_URL.rstrip("/")
SANDBOX_OTP = settings.MULTICARD_SANDBOX_OTP
USE_SANDBOX = settings.MULTICARD_USE_SANDBOX


def mentor_create_payout(mentor_profile, amount, invoice_id, device_details=None, confirmable=True):
    user = mentor_profile.user

    # REQUIRED FIELDS CHECK
    required_fields = {
        "card_number": mentor_profile.card_number,
        "passport_number": mentor_profile.passport_number,
        "dob": mentor_profile.dob,
        "pinfl": mentor_profile.pinfl,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "middle_name": user.middle_name,
        "passport_expiry_date": mentor_profile.passport_expiry_date,
        "address": mentor_profile.address,
    }

    missing = [k for k, v in required_fields.items() if not v]
    if missing:
        return {
            "success": False,
            "error": {
                "code": "MISSING_FIELDS",
                "details": f"Quyidagi maydonlar to‘ldirilmagan: {', '.join(missing)}"
            }
        }

    # TOKEN OLISH
    token = multicard_get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # KYC DATA
    kyc_data = {
        "last_name": user.last_name,
        "first_name": user.first_name,
        "middle_name": user.middle_name or "",
        "passport": mentor_profile.passport_number,
        "pinfl": mentor_profile.pinfl,
        "dob": mentor_profile.dob.strftime("%Y-%m-%d"),
        "passport_expiry_date": mentor_profile.passport_expiry_date.strftime("%Y-%m-%d"),
    }

    device_details = device_details or {
        "ip": "127.0.0.1",
        "user_agent": "python-requests"
    }

    payload = {
        "card": {"pan": mentor_profile.card_number},
        "amount": int(amount * 100),
        "store_id": settings.MULTICARD_STORE_ID,
        "invoice_id": str(invoice_id),
        "confirmable": confirmable,
        "device_details": device_details,
        "kyc_data": kyc_data,
    }

    # STEP 1: CREATE PAYOUT WITH ERROR HANDLING
    try:
        resp = requests.post(
            f"{API_URL}/payment/credit",
            json=payload,
            headers=headers,
            timeout=30
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("❌ STATUS:", resp.status_code)
        print("❌ HEADERS:", resp.headers)
        print("❌ TEXT:", resp.text)
        try:
            print("❌ JSON:", resp.json())
        except:
            print("❌ JSON PARSE ERROR")
        return {
            "success": False,
            "error": resp.text
        }


    data = resp.json()

    # STEP 2: CONFIRM IF SANDBOX
    if confirmable and USE_SANDBOX:
        payment_uuid = data.get("data", {}).get("uuid")
        if payment_uuid:
            try:
                confirm_resp = requests.put(
                    f"{API_URL}/payment/credit/{payment_uuid}",
                    json={"otp": SANDBOX_OTP},
                    headers=headers,
                    timeout=30
                )
                confirm_resp.raise_for_status()
                data["confirmed"] = confirm_resp.json()
            except requests.exceptions.HTTPError as e:
                print("❌ CONFIRM ERROR:", confirm_resp.text)
                return {
                    "success": False,
                    "error": confirm_resp.json() if confirm_resp.text else str(e)
                }

    # STEP 3: UPDATE BALANCE
    balance, _ = MentorBalance.objects.get_or_create(mentor=user)
    balance.balance -= amount
    balance.save()

    MentorBalanceHistory.objects.create(
        mentor=user,
        amount=-amount,
        description=f"Multicard orqali yechib olindi, WithdrawRequest #{invoice_id}"
    )

    data["success"] = True
    return data
