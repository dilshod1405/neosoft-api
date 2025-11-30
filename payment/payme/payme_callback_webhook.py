from payme.views import PaymeWebHookAPIView
from rest_framework.permissions import AllowAny
from payment.models import Transaction, Enrollment
from django.utils import timezone as dj_timezone
from datetime import timezone


class PaymeCallBackAPIView(PaymeWebHookAPIView):
    permission_classes = [AllowAny]

    def _ok(self, data: dict):
        return {"result": data}

    def _error(self, code: int, message: str, data=None):
        err = {
            "error": {
                "code": code,
                "message": {
                    "uz": message,
                    "ru": message,
                    "en": message,
                }
            }
        }
        if data is not None:
            err["error"]["data"] = data
        return err




    def _get_local_tx_by_account(self, params):
        try:
            return Transaction.objects.get(
                id=int(params["account"]["id"]), provider="payme"
            )
        except Transaction.DoesNotExist:
            return None




    def _get_local_tx_by_payme_id(self, payme_id: str):
        return Transaction.objects.filter(
            transaction_id=payme_id, provider="payme"
        ).first()
    



    # ---------- CheckPerformTransaction ----------
    def check_perform_transaction(self, params, *args, **kwargs):
        tx = self._get_local_tx_by_account(params)
        if not tx:
            return self._error(-31050, "Transaction not found")

        incoming = int(params["amount"])
        expected = tx.amount * 100
        if incoming != expected:
            return self._error(-31001, "Incorrect amount")

        return self._ok({"allow": True})
    



    # ---------- CreateTransaction ----------
    def create_transaction(self, params, *args, **kwargs):
        tx = self._get_local_tx_by_account(params)
        if not tx:
            return self._error(-31050, "Transaction not found")

        incoming = int(params["amount"])
        expected = tx.amount * 100
        if incoming != expected:
            return self._error(-31001, "Incorrect amount")

        if tx.status == "SUCCESS":
            return self._error(-31008, "Transaction already paid")
        if tx.status == "CANCELLED":
            return self._error(-31007, "Transaction cancelled")

        payme_id = params["id"]

        if not tx.metadata:
            tx.metadata = {}

        if not tx.transaction_id:
            tx.transaction_id = payme_id
            tx.status = "PENDING"
            now_ms = int(dj_timezone.now().timestamp() * 1000)
            tx.metadata["payme_create_time"] = now_ms
            tx.save(update_fields=["transaction_id", "status", "metadata", "updated_at"])
        else:
            if tx.transaction_id != payme_id:
                return self._error(-31099, "Transaction already exists", data=tx.transaction_id)
            if "payme_create_time" not in tx.metadata or not tx.metadata["payme_create_time"]:
                tx.metadata["payme_create_time"] = int(dj_timezone.now().timestamp() * 1000)
                tx.save(update_fields=["metadata", "updated_at"])

        create_time = int(tx.metadata.get("payme_create_time"))

        return self._ok({
            "transaction": tx.transaction_id,
            "state": 1,
            "create_time": create_time,
        })
    



    # ---------- PerformTransaction ----------
    def perform_transaction(self, params, *args, **kwargs):
        payme_id = params["id"]
        tx = self._get_local_tx_by_payme_id(payme_id)
        if not tx:
            return self._error(-31003, "Transaction not found")

        if not tx.perform_time:  # idempotent
            tx.status = "SUCCESS"
            tx.perform_time = dj_timezone.now()
            tx.save(update_fields=["status", "perform_time", "updated_at"])
            Enrollment.objects.get_or_create(student=tx.order.student, course=tx.order.course)

        return self._ok({
            "transaction": tx.transaction_id,
            "state": 2,
            "perform_time": int(tx.perform_time.timestamp() * 1000),
        })
    




    # ---------- CheckTransaction ----------
    def check_transaction(self, params, *args, **kwargs):
        payme_id = params["id"]
        tx = self._get_local_tx_by_payme_id(payme_id)
        if not tx:
            return self._error(-31003, "Transaction not found")

        create_time = tx.metadata.get("payme_create_time")
        if not create_time:
            create_time = int(tx.created_at.timestamp() * 1000)

        perform_time = int(tx.perform_time.timestamp() * 1000) if tx.perform_time else 0
        cancel_time = int(tx.cancel_time.timestamp() * 1000) if tx.cancel_time else 0

        if tx.cancel_time:
            state = -2 if tx.perform_time else -1
        elif tx.perform_time:
            state = 2
        else:
            state = 1

        return self._ok({
            "create_time": create_time,
            "perform_time": perform_time,
            "cancel_time": cancel_time,
            "transaction": tx.transaction_id,
            "state": state,
            "reason": tx.cancel_reason if tx.cancel_time else None,
        })
    




    # ---------- Cancel ransaction ----------
    def cancel_transaction(self, params, *args, **kwargs):
        payme_id = params["id"]
        reason = params.get("reason")
        tx = self._get_local_tx_by_payme_id(payme_id)
        if not tx:
            return self._error(-31003, "Transaction not found")

        was_performed = tx.perform_time is not None

        if tx.cancel_time:
            return self._ok({
                "transaction": tx.transaction_id,
                "state": -2 if was_performed else -1,
                "cancel_time": int(tx.cancel_time.timestamp() * 1000),
                "reason": tx.cancel_reason,
            })

        tx.status = "CANCELLED"
        tx.cancel_reason = reason
        tx.cancel_time = dj_timezone.now()
        tx.save(update_fields=["status", "cancel_reason", "cancel_time", "updated_at"])

        return self._ok({
            "transaction": tx.transaction_id,
            "state": -2 if was_performed else -1,
            "cancel_time": int(tx.cancel_time.timestamp() * 1000),
            "reason": reason,
        })
    
    



    # ---------- GetStatement ----------
    def get_statement(self, params, *args, **kwargs):
        date_from = int(params.get("from"))
        date_to = int(params.get("to"))

        # Payme timestamp (ms) -> Python datetime UTC
        from_dt = dj_timezone.datetime.fromtimestamp(date_from / 1000, tz=timezone.utc)
        to_dt = dj_timezone.datetime.fromtimestamp(date_to / 1000, tz=timezone.utc)

        tx_list = (
            Transaction.objects.filter(
                provider="payme",
                transaction_id__isnull=False,
                metadata__has_key="payme_create_time",
            )
            .order_by("metadata__payme_create_time")
        )

        result = []
        for tx in tx_list:
            created_ms = tx.metadata.get("payme_create_time")
            if not created_ms:
                continue

            created_dt = dj_timezone.datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
            if not (from_dt <= created_dt <= to_dt):
                continue

            perform_time = int(tx.perform_time.timestamp() * 1000) if tx.perform_time else 0
            cancel_time = int(tx.cancel_time.timestamp() * 1000) if tx.cancel_time else 0

            if tx.cancel_time:
                state = -2 if tx.perform_time else -1
            elif tx.perform_time:
                state = 2
            else:
                state = 1

            result.append({
                "id": tx.transaction_id,
                "time": created_ms,
                "amount": tx.amount,
                "account": {"id": tx.id},
                "create_time": created_ms,
                "perform_time": perform_time,
                "cancel_time": cancel_time,
                "transaction": str(tx.id),
                "state": state,
                "reason": tx.cancel_reason,
                "receivers": [],
            })

        return self._ok({"transactions": result})

