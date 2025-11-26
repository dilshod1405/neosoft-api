from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import exceptions
from utils.get_redis import get_redis
from authentication.backends import get_client_ip

# ==================================================================
#       ACCESS TOKEN AUTHENTICATION + SINGLE DEVICE & SINGLE IP
# ==================================================================

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if not result:
            return None

        user, token = result
        jti = token.payload.get("jti")
        ip = get_client_ip(request)

        session_key_user = f"user_session:{user.id}"
        session_key_ip = f"ip_session:{ip}"

        user_session = get_redis.get(session_key_user)
        if user_session:
            old_jti, old_ip = user_session.decode().split(":")
            if old_jti != jti or old_ip != ip:
                raise exceptions.AuthenticationFailed("Session expired — new login detected.")

        ip_session = get_redis.get(session_key_ip)
        if ip_session:
            old_user_id, _ = ip_session.decode().split(":")
            if str(old_user_id) != str(user.id):
                raise exceptions.AuthenticationFailed("This IP is already used by another user.")

        return (user, token)


def store_user_session(user_id, jti, ip, ttl):
    session_value = f"{jti}:{ip}"
    get_redis.setex(f"user_session:{user_id}", ttl, session_value)
    get_redis.setex(f"ip_session:{ip}", ttl, f"{user_id}:{jti}")
