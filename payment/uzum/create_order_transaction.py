from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from content.models import Course
from payment.models import Order, Transaction
from payment.serializers import OrderSerializer, TransactionSerializer

class CreateOrderTransactionUzumAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course = get_object_or_404(Course, id=request.data.get("course_id"))
        provider = request.data.get("provider")  # payme | uzum | click

        order = Order.create_with_final_price(student=request.user, course=course)
        transaction = Transaction.create_from_order(order, provider=provider)

        return Response({
            "order": OrderSerializer(order).data,
            "transaction": TransactionSerializer(transaction).data,
        })
