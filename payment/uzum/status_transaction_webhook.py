from django.http import JsonResponse
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
class UzumStatusView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            service_id = data["serviceId"]
            trans_id = data["transId"]

            tx = Transaction.objects.filter(
                transaction_id=trans_id,
                provider="uzum"
            ).first()

            if not tx:
                return JsonResponse(uz_error(10014, "Transaction not found"))

            if tx.status == "SUCCESS":
                state = "CONFIRMED"
            elif tx.status == "CANCELLED":
                state = "REVERSED"
            else:
                state = "CREATED"

            create_time = (
                tx.metadata.get("uzum_create_time")
                if tx.metadata else int(tx.created_at.timestamp() * 1000)
            )

            return JsonResponse(uz_ok({
                "serviceId": service_id,
                "transId": trans_id,
                "status": state,
                "transTime": create_time,
                "confirmTime": int(tx.perform_time.timestamp() * 1000) if tx.perform_time else None,
                "reverseTime": int(tx.cancel_time.timestamp() * 1000) if tx.cancel_time else None,
                "amount": tx.amount * 100
            }))

        except Exception as e:
            return JsonResponse(uz_error(99999, str(e)))
