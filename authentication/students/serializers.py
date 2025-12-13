from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "middle_name",
            "full_name",
            "phone",
            "photo",
            "is_verified",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "is_verified",
            "date_joined",
        )
