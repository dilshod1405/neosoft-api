from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from payment.models import Course
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from payment.serializers import OrderSerializer, TransactionSerializer
from payment.models import Transaction, Order
from click_up import ClickUp



class CreateClickOrderTransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course = get_object_or_404(Course, id=request.data.get("course_id"))

        order = Order.create_with_final_price(
            student=request.user,
            course=course
        )

        transaction = Transaction.create_from_order(order, provider="click")

        click = ClickUp(
            service_id=settings.CLICK_SERVICE_ID,
            merchant_id=settings.CLICK_MERCHANT_ID,
            secret_key=settings.CLICK_SECRET_KEY,
        )

        payment_url = click.initializer.generate_pay_link(
            id=transaction.id,
            amount=transaction.amount,
            return_url="https://edu.neosoft.uz/"
        )

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(transaction).data,
            "payment_url": payment_url
        })