# payment/student/serializers.py

from rest_framework import serializers
from payment.models import Transaction

class StudentTransactionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="order.course.title_uz", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "provider",
            "amount",
            "status",
            "created_at",
            "course_title",
        ]
        read_only_fields = fields
