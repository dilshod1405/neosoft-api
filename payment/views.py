from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import PlatformBalance, PlatformBalanceHistory
from .serializers import PlatformBalanceDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from content.models import Course
from payment.models import Order, Transaction
from payment.serializers import OrderSerializer, TransactionSerializer
from payme import Payme
from click_up import ClickUp


class PlatformBalanceDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PlatformBalanceDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        balance = PlatformBalance.objects.get(id=1)
        history = PlatformBalanceHistory.objects.all().order_by("-created_at")

        return {
            "balance": balance,
            "history": history
        }


class CreateUniversalPaymentAPIView(APIView):
    """
    Single endpoint to create Order & Transaction,
    and return payment link for Payme, Click, or Uzum.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get("course_id")
        provider = request.data.get("provider")

        if provider not in ["payme", "click", "uzum"]:
            return Response({"error": "Invalid provider"}, status=400)

        course = get_object_or_404(Course, id=course_id)

        # ✅ TO‘G‘RI: oddiy create
        order = Order.objects.create(
            student=request.user,
            course=course
        )
        # ↑ final_price avtomatik save() ichida hisoblanadi

        # ✅ Transaction ham to‘g‘ri yaratiladi
        transaction = Transaction.create_from_order(
            order=order,
            provider=provider
        )

        payment_url = None

        # PAYME
        if provider == "payme":
            payme = Payme(settings.PAYME_ID, settings.PAYME_KEY)
            payment_url = payme.initializer.generate_pay_link(
                id=str(transaction.id),
                amount=transaction.amount,
                return_url="https://edu.neosoft.uz/"
            )

        # CLICK
        elif provider == "click":
            click = ClickUp(
                service_id=settings.CLICK_SERVICE_ID,
                merchant_id=settings.CLICK_MERCHANT_ID,
                secret_key=settings.CLICK_SECRET_KEY,
            )
            payment_url = click.initializer.generate_pay_link(
                id=str(transaction.id),
                amount=transaction.amount,
                return_url="https://edu.neosoft.uz/"
            )

        # UZUM PAY
        elif provider == "uzum":
            payment_url = f"https://pay.uzum.com/pay/{transaction.id}"

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(transaction).data,
            "payment_url": payment_url
        })
