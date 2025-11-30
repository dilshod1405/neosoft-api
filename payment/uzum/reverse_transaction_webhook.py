from django.http import JsonResponse
from django.utils import timezone as dj_timezone
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from payment.models import Transaction


def uz_error(code, msg):
    return {
        "error": {
            "code": code,
            "message": {"uz": msg, "ru": msg, "en": msg}
        }
    }


def uz_ok(data):
    return {"result": data}


@method_decorator(csrf_exempt, name='dispatch')
class UzumReverseView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            trans_id = data["transId"]
            service_id = data["serviceId"]

            tx = Transaction.objects.filter(
                transaction_id=trans_id,
                provider="uzum"
            ).first()

            if not tx:
                return JsonResponse(uz_error(10014, "Transaction not found"))

            if tx.status == "CANCELLED":
                return JsonResponse(uz_ok({
                    "serviceId": service_id,
                    "transId": trans_id,
                    "status": "REVERSED",
                    "reverseTime": int(tx.cancel_time.timestamp() * 1000),
                    "amount": tx.amount * 100
                }))

            tx.status = "CANCELLED"
            tx.cancel_time = dj_timezone.now()
            tx.save(update_fields=["status", "cancel_time"])

            return JsonResponse(uz_ok({
                "serviceId": service_id,
                "transId": trans_id,
                "status": "REVERSED",
                "reverseTime": int(tx.cancel_time.timestamp() * 1000),
                "amount": tx.amount * 100
            }))

        except Exception as e:
            return JsonResponse(uz_error(99999, str(e)))
