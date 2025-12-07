from rest_framework import serializers
from payment.mentors.models import WithdrawRequest

class WithdrawRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawRequest
        fields = [
            "id",
            "mentor",
            "amount",
            "status",
            "created_at",
            "resolved_at",
            "note",
            "multicard_transaction_id",
            "multicard_uuid",
        ]
        read_only_fields = [
            "mentor",
            "status",
            "multicard_transaction_id",
            "multicard_uuid",
            "resolved_at",
            "note",
        ]
