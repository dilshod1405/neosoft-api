from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from utils.get_redis import get_redis

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result

        device_id = request.COOKIES.get("device_id")
        if not device_id:
            raise AuthenticationFailed("Device ID not found")

        redis = get_redis()
        saved_device = redis.get(f"user_device:{user.id}")

        if not saved_device or saved_device != device_id:
            raise AuthenticationFailed("Device mismatch")

        return (user, token)
