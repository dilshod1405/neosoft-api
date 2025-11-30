from rest_framework import serializers
from payment.models import Order, Transaction


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "course", "student", "final_price", "status"]
        read_only_fields = ["id", "student", "final_price", "status"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ["id", "order", "amount", "status", "provider", "created_at"]
        read_only_fields = ["id", "status", "created_at"]