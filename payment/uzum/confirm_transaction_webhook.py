
from payment.models import Transaction
from django.http import JsonResponse
from django.utils import timezone as dj_timezone
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from content.models import Enrollment


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
class UzumConfirmView(View):
    def post(self, request):
        data = json.loads(request.body)
        trans_id = data["transId"]

        tx = Transaction.objects.filter(transaction_id=trans_id, provider="uzum").first()
        if not tx:
            return JsonResponse(uz_error(10014, "Transaction not found"))

        if tx.status == "SUCCESS":
            return JsonResponse(uz_ok({
                "transId": trans_id,
                "status": "CONFIRMED",
                "confirmTime": int(tx.perform_time.timestamp() * 1000),
            }))

        tx.status = "SUCCESS"
        tx.perform_time = dj_timezone.now()
        tx.save()

        Enrollment.objects.get_or_create(
            student=tx.order.student,
            course=tx.order.course
        )

        return JsonResponse(uz_ok({
            "transId": trans_id,
            "status": "CONFIRMED",
            "confirmTime": int(tx.perform_time.timestamp() * 1000),
        }))
