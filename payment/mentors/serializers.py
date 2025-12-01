from rest_framework import serializers
from payment.models import Transaction
from .models import MentorBalanceHistory, MentorBalance, WithdrawRequest

class MentorTransactionSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source="order.student.full_name", read_only=True)
    course = serializers.CharField(source="order.course.title_uz", read_only=True)
    mentor_share = serializers.SerializerMethodField()
    platform_share = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "amount",
            "mentor_share",
            "platform_share",
            "status",
            "created_at",
            "perform_time",
            "cancel_time",
            "student",
            "course",
        ]

    def get_mentor_share(self, obj):
        return f"{obj.mentor_share:,} so'm" if obj.mentor_share else None

    def get_platform_share(self, obj):
        return f"{obj.platform_share:,} so'm" if obj.platform_share else None


class MentorBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorBalance
        fields = ["balance", "updated_at"]


class MentorBalanceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorBalanceHistory
        fields = ["amount", "description", "created_at"]


class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = ["amount", "status", "created_at", "resolved_at", "note"]
