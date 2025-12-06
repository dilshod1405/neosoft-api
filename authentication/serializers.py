from rest_framework import serializers
from validators.validate_uzbek_phone import validate_uzbek_phone
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.get_redis import get_redis
from utils.get_client_ip import get_client_ip
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
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            if len(password) < 8:
                raise serializers.ValidationError({'password': 'Password must be at least 8 characters long.'})
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

        # Userni topish
        user = None
        if email:
            user = CustomUser.objects.filter(email=email.lower().strip()).first()
        if not user and phone:
            user = CustomUser.objects.filter(phone=phone).first()

        if not user:
            raise serializers.ValidationError({"detail": "Foydalanuvchi topilmadi."})

        if not user.check_password(password):
            raise serializers.ValidationError({"detail": "Parol noto'g'ri."})

        if not user.is_verified:
            raise serializers.ValidationError({"detail": "Akkaunt tasdiqlanmagan."})

        request = self.context.get("request")
        ip = get_client_ip(request)

        
        try:
            if ip.startswith("127.") or ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172."):
                logger.warning(f"LOCAL IP detected ({ip}) — skipping GeoIP check")
            else:
                from django.contrib.gis.geoip2 import GeoIP2
                gi = GeoIP2()
                country = gi.country(ip)["country_code"]
                print("COUNTRY:", country, flush=True)
                logger.warning(f"COUNTRY: {country}")
                if country != "UZ":
                    raise serializers.ValidationError({"detail": "O'zbekistondan tashqarida login qilish mumkin emas."})

        except Exception as e:
            logger.error(f"GEOIP ERROR: {e}")
            print("GEOIP ERROR:", e, flush=True)



        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        jti = refresh["jti"]

        redis_client = get_redis()

        ttl = 7 * 24 * 60 * 60  # 7 kun

        redis_client.delete(f"user_session:{user.id}")
        redis_client.delete(f"ip_session:{ip}")

        redis_client.setex(f"user_session:{user.id}", ttl, f"{jti}:{ip}")
        redis_client.setex(f"ip_session:{ip}", ttl, f"{user.id}:{jti}")

        return {
            "refresh": str(refresh),
            "access": access,
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
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