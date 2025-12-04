import requests
from django.conf import settings
from payment.mentors.models import MentorBalanceHistory, MentorBalance

API_URL = getattr(settings, "MULTICARD_API_URL", "https://dev-mesh.multicard.uz")
API_KEY = getattr(settings, "MULTICARD_API_KEY", "")
SANDBOX_OTP = getattr(settings, "MULTICARD_SANDBOX_OTP", "112233")
USE_SANDBOX = getattr(settings, "MULTICARD_USE_SANDBOX", True)


def mentor_create_payout(mentor_profile, amount, invoice_id, device_details=None, confirmable=True):
    user = mentor_profile.user

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
        return {"success": False, "error": {"code": "MISSING_FIELDS", "details": f"Quyidagi maydonlar to‘ldirilmagan: {', '.join(missing)}"}}

    kyc_data = {
        "last_name": user.last_name,
        "first_name": user.first_name,
        "middle_name": user.middle_name or "",
        "passport": mentor_profile.passport_number,
        "pinfl": mentor_profile.pinfl,
        "dob": mentor_profile.dob.strftime("%Y-%m-%d"),
        "passport_expiry_date": mentor_profile.passport_expiry_date.strftime("%Y-%m-%d"),
    }

    device_details = device_details or {"ip": "127.0.0.1", "user_agent": "python-requests"}

    payload = {
        "card": {"pan": mentor_profile.card_number},
        "amount": int(amount * 100),
        "store_id": getattr(settings, "MULTICARD_STORE_ID", 1),
        "invoice_id": str(invoice_id),
        "confirmable": confirmable,
        "device_details": device_details,
        "kyc_data": kyc_data,
    }

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    resp = requests.post(f"{API_URL}/payment/credit", json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if confirmable and USE_SANDBOX:
        payment_uuid = data.get("data", {}).get("uuid")
        if payment_uuid:
            confirm_resp = requests.put(
                f"{API_URL}/payment/credit/{payment_uuid}",
                json={"otp": SANDBOX_OTP},
                headers=headers,
                timeout=30
            )
            confirm_resp.raise_for_status()
            data["confirmed"] = confirm_resp.json()

    # Withdraw balansini yangilash
    balance, _ = MentorBalance.objects.get_or_create(mentor=user)
    balance.balance -= amount
    balance.save()

    MentorBalanceHistory.objects.create(
        mentor=user,
        amount=-amount,
        description=f"Multicard orqali yechib olindi, WithdrawRequest #{invoice_id}"
    )

    return data
