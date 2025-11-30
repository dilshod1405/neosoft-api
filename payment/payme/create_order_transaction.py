from payme import Payme
from django.conf import settings
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from content.models import Course
from payment.models import Order, Transaction
from ..serializers import OrderSerializer, TransactionSerializer


# ==================================================================
#                 CREATE ORDER AND TRANSACTION
# ==================================================================

class CreateOrderTransactionAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=request.data.get("course_id"))
        provider = request.data.get("provider")

        order = Order.create_with_final_price(student=request.user, course=course)
        transaction = Transaction.create_from_order(order, provider="payme")

        payme = Payme(settings.PAYME_ID, settings.PAYME_KEY)
        pay_link = payme.initializer.generate_pay_link(
            id=str(transaction.id),
            amount=transaction.amount,  # integer tiyin
            return_url="https://edu.neosoft.uz/"
        )

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(transaction).data,
            "pay_link": pay_link,
        })
