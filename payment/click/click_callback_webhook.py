# payment/click/click_callback_webhook.py

from click_up.views import ClickWebhook
from payment.models import Transaction
from content.models import Enrollment
from django.utils import timezone as dj_timezone
import logging

logger = logging.getLogger(__name__)

class ClickCallBackAPIView(ClickWebhook):

    def _ok(self, data: dict):
        return {"result": data}

    def _error(self, code: int, message: str):
        return {
            "error": {
                "code": code,
                "message": {
                    "uz": message,
                    "ru": message,
                    "en": message
                }
            }
        }

    # ------------------------------------------------------
    # Получение локальной транзакции
    # ------------------------------------------------------
    def _get_local_tx(self, params):
        try:
            return Transaction.objects.get(
                id=int(params["merchant_trans_id"]),
                provider="click"
            )
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {params.get('merchant_trans_id')}")
            return None

    # ------------------------------------------------------
    # Prepare (CheckPerformTransaction)
    # ------------------------------------------------------
    def prepare(self, params):
        tx = self._get_local_tx(params)
        if not tx:
            return self._error(-5, "Transaction not found")

        incoming = int(params["amount"])
        expected = tx.amount

        if incoming != expected:
            return self._error(-2, "Invalid amount")

        if not tx.metadata:
            tx.metadata = {}

        if "click_prepare_time" not in tx.metadata:
            tx.metadata["click_prepare_time"] = int(dj_timezone.now().timestamp() * 1000)
            tx.status = "PENDING"
            tx.save(update_fields=["metadata", "status", "updated_at"])

        logger.info(f"Click Prepare OK: tx_id={tx.id}, amount={tx.amount}")
        return self._ok({"prepare_id": str(tx.id)})

    # ------------------------------------------------------
    # Complete (PerformTransaction)
    # ------------------------------------------------------
    def complete(self, params):
        tx = self._get_local_tx(params)
        if not tx:
            return self._error(-6, "Transaction not found")

        if not tx.perform_time:
            tx.perform_time = dj_timezone.now()
            tx.status = "SUCCESS"
            tx.save(update_fields=["perform_time", "status", "updated_at"])

            # Запись студента в курс
            Enrollment.objects.get_or_create(
                student=tx.order.student,
                course=tx.order.course
            )

        logger.info(f"Click Complete OK: tx_id={tx.id}, perform_time={tx.perform_time}")
        return self._ok({
            "transaction": str(tx.id),
            "perform_time": int(tx.perform_time.timestamp() * 1000)
        })

    # ------------------------------------------------------
    # Логи успешной и отмененной оплаты
    # ------------------------------------------------------
    def successfully_payment(self, params):
        logger.info(f"Click payment SUCCESS: {params}")

    def cancelled_payment(self, params):
        logger.warning(f"Click payment CANCELLED: {params}")
