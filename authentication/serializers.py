from rest_framework import serializers
from validators.validate_uzbek_phone import validate_uzbek_phone
from .models import CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from utils.get_redis import get_redis
from utils.get_client_ip import get_client_ip

User = CustomUser

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(required=False, allow_blank=True, validators=[validate_uzbek_phone])

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
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




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')
        password = attrs.get('password')

        user = None
        if email:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                pass
        if not user and phone:
            try:
                user = CustomUser.objects.get(phone=phone)
            except CustomUser.DoesNotExist:
                pass

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_verified:
            raise serializers.ValidationError("Account is not verified.")

        # Generate JWT tokens
        refresh = self.get_token(user)
        access = str(refresh.access_token)
        jti = refresh["jti"]

        ip = get_client_ip(self.context.get("request"))
        ttl = 7 * 24 * 60 * 60
        get_redis.delete(f"user_session:{user.id}")
        get_redis.delete(f"ip_session:{ip}")

        get_redis.setex(f"user_session:{user.id}", ttl, f"{jti}:{ip}")
        get_redis.setex(f"ip_session:{ip}", ttl, f"{user.id}:{jti}")

        return {
            "refresh": str(refresh),
            "access": access,
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "is_mentor": user.is_mentor,
            },
        }




class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)