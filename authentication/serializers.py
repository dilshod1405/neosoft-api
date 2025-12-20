from rest_framework import serializers
import uuid
from validators.validate_uzbek_phone import validate_uzbek_phone
from .models import CustomUser
from utils.get_redis import get_redis
from rest_framework_simplejwt.tokens import RefreshToken

User = CustomUser

import logging
logger = logging.getLogger(__name__)



# ============================================================
#                  USER REGISTER SERIALIZER
# ============================================================

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(required=False, allow_blank=True, validators=[validate_uzbek_phone])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'password', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'middle_name': {'required': True},
            'password': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Bu email platformada allaqachon mavjud")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            if len(password) < 6:
                raise serializers.ValidationError({'password': "Parol uzunligi 6 ta belgidan kam bo'lmasligi kerak"})
        return attrs





# ============================================================
#                  USER LOGIN SERIALIZER
# ============================================================

class CustomLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        phone = attrs.get("phone")
        password = attrs.get("password")

        if not email and not phone:
            raise serializers.ValidationError({"detail": "Email yoki telefon kiriting."})

        user = None
        if email:
            user = CustomUser.objects.filter(email=email.lower().strip()).first()
        if not user and phone:
            user = CustomUser.objects.filter(phone=phone).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError({"detail": "Login yoki parol noto‘g‘ri."})

        if not user.is_verified:
            raise serializers.ValidationError({"detail": "Akkaunt tasdiqlanmagan."})

        # 🔐 device_id generatsiya
        device_id = str(uuid.uuid4())

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        redis = get_redis()
        ttl = 7 * 24 * 60 * 60  # 7 kun
        redis.setex(f"user_device:{user.id}", ttl, device_id)

        return {
            "refresh": str(refresh),
            "access": access,
            "device_id": device_id,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "is_mentor": user.is_mentor,
            },
        }









# ============================================================
#                  RESEND OTP CODE SERIALIZER
# ============================================================

class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)