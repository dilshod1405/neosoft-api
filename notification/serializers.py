from rest_framework import serializers
from .models import Notification


class NotificationCreateSerializer(serializers.Serializer):
    target = serializers.ChoiceField(choices=["mentor", "student", "all"])
    type = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    metadata = serializers.JSONField(required=False)
    action_url = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    valid_until = serializers.DateTimeField(required=False, allow_null=True)




class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "type",
            "title",
            "message",
            "metadata",
            "action_url",
            "is_read",
            "read_at",
            "valid_until",
            "created_at",
        ]
        read_only_fields = fields