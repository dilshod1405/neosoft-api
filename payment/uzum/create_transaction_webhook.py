from payment.models import Transaction
from django.http import JsonResponse
from django.utils import timezone as dj_timezone
import json
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
class UzumCreateView(View):
    def post(self, request):
        data = json.loads(request.body)

        account_id = data["params"]["account"]
        tx = Transaction.objects.filter(id=account_id, provider="uzum").first()
        if not tx:
            return JsonResponse(uz_error(10007, "Transaction not found"))

        amount = data["amount"]
        expected = tx.amount * 100

        if amount != expected:
            return JsonResponse(uz_error(10011, "Amount mismatch"))

        uzum_trans_id = data["transId"]

        # idempotent
        if tx.transaction_id and tx.transaction_id != uzum_trans_id:
            return JsonResponse(uz_error(10010, "Transaction already exists"))

        if not tx.transaction_id:
            tx.transaction_id = uzum_trans_id
            tx.metadata = {
                "uzum_create_time": int(dj_timezone.now().timestamp() * 1000)
            }
            tx.save()

        return JsonResponse(uz_ok({
            "transId": uzum_trans_id,
            "status": "CREATED",
            "transTime": tx.metadata["uzum_create_time"]
        }))
