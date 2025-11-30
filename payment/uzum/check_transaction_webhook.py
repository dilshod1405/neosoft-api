import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
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
class UzumCheckView(View):
    def post(self, request):
        data = json.loads(request.body)

        account_id = data["params"]["account"]
        tx = Transaction.objects.filter(id=account_id, provider="uzum").first()
        if not tx:
            return JsonResponse(uz_error(10007, "Transaction not found"))

        incoming = data["amount"]
        expected = tx.amount * 100  # so‘m → tiyin

        if incoming != expected:
            return JsonResponse(uz_error(10011, "Incorrect amount"))

        return JsonResponse(uz_ok({"status": "OK"}))

