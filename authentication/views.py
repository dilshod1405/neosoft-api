from .models import CustomUser
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import RegisterUserSerializer, CustomLoginSerializer, ResendCodeSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from emails.auth.activation_code_email import activation_code_email
from utils.get_redis import get_redis
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
User = CustomUser
from i18n.util import t, get_language_from_path
from rest_framework_simplejwt.exceptions import InvalidToken
from django.conf import settings

import logging
logger = logging.getLogger(__name__)



# ============================================================
#                  REGISTRAION USER VIEW
# ============================================================

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        language = get_language_from_path(request.path)

        email = request.data.get("email")
        existing = User.objects.filter(email=email).first()

        if existing and existing.is_verified:
            return Response(
                {"detail": t("auth.already_registered", language)},
                status=status.HTTP_400_BAD_REQUEST
            )

        if existing and not existing.is_verified:
            errors = {}

            if existing.first_name != request.data.get("first_name"):
                errors["first_name"] = t("auth.first_name_mismatch", language)

            if existing.last_name != request.data.get("last_name"):
                errors["last_name"] = t("auth.last_name_mismatch", language)

            if existing.middle_name != request.data.get("middle_name"):
                errors["middle_name"] = t("auth.middle_name_mismatch", language)

            if existing.phone != request.data.get("phone"):
                errors["phone"] = t("auth.phone_mismatch", language)

            if errors:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

            activation_code_email.delay(existing.id, language)

            return Response(
                {
                    "message": t("auth.not_verified_resent", language),
                    "email": existing.email,
                },
                status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create_user(
            **serializer.validated_data,
            is_active=False,
            is_verified=False,
        )
        activation_code_email.delay(user.id, language)
        return Response(
            {
                "message": "Ro'yxatdan o'tildi. Emailga kod yuborildi.",
                "email": user.email,
            },
            status=status.HTTP_201_CREATED,
        )





# ============================================================
#                  USER LOGIN VIEW
# ============================================================

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomLoginSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        refresh = data.pop("refresh")

        response = Response(data)

        response.set_cookie(
            key="refresh",
            value=refresh,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
            path="/",
            max_age=7 * 24 * 60 * 60,
        )


        return response





# ============================================================
#                  REFRESH TOKEN VIEW
# ============================================================

@method_decorator(csrf_exempt, name="dispatch")
class RefreshView(TokenRefreshView):

    def post(self, request, *args, **kwargs):
        print("=== REFRESH DEBUG ===")
        print("COOKIES:", request.COOKIES)
        print("HEADERS:", dict(request.headers))
        refresh_token = request.COOKIES.get("refresh")

        if not refresh_token:
            raise InvalidToken("Refresh token not found")

        request._full_data = {"refresh": refresh_token}


        response = super().post(request, *args, **kwargs)

        if response.status_code != 200:
            return response

        try:
            token_obj = RefreshToken(refresh_token)
            jti = token_obj["jti"]
            user_id = token_obj["user_id"]
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        ip = request.META.get("REMOTE_ADDR")
        redis = get_redis()

        session = redis.get(f"user_session:{user_id}")
        if session:
            old_jti, old_ip = session.split(":")

            if old_ip != ip or old_jti != jti:
                return Response(
                    {
                        "detail": (
                            "Qurilma ishi to‘xtatildi — "
                            "yangi qurilmadan kirish aniqlandi."
                        )
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        ttl = 7 * 24 * 60 * 60
        redis.setex(f"user_session:{user_id}", ttl, f"{jti}:{ip}")
        redis.setex(f"ip_session:{ip}", ttl, f"{user_id}:{jti}")

        return response
    





# ============================================================
#                  ACCOUNT ACTIVATION VIEW
# ============================================================


def get_stored_code(user_id: int) -> str | None:
    code = get_redis().get(f"activation_code:{user_id}")
    return code if code else None

def clear_stored_code(user_id: int) -> None:
    get_redis().delete(f"activation_code:{user_id}")


class ActivationView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        language = get_language_from_path(request.path)

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"detail": t("common.required_fields", language)},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email, is_verified=False)
            stored_code = get_stored_code(user.id)

            if stored_code == code:
                user.is_verified = True
                user.is_active = True
                user.save(update_fields=["is_verified", "is_active"])
                clear_stored_code(user.id)

                refresh = RefreshToken.for_user(user)

                return Response(
                    {
                        "message": t("auth.activation_success", language),
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "first_name": user.first_name,
                            "last_name": user.last_name,
                            "middle_name": user.middle_name,
                            "photo": user.photo.url if user.photo else None,
                            "is_mentor": user.is_mentor,
                            "is_verified": user.is_verified,
                        }
                    }
                )

            return Response(
                {"detail": t("auth.activation_code_invalid", language)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"detail": t("auth.activation_user_not_found", language)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {"detail": t("auth.activation_failed", language)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




# ============================================================
#                  RESEND ACTIVATION CODE VIEW
# ============================================================

class ResendCodeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendCodeSerializer

    def create(self, request, *args, **kwargs):
        language = get_language_from_path(request.path)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=email, is_verified=False)

            clear_stored_code(user.id)
            activation_code_email.delay(user.id, language)

            return Response(
                {"message": t("auth.resend_success", language)},
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"detail": t("auth.resend_not_found", language)},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {"detail": t("auth.resend_failed", language)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





# ============================================================
#                  USER LOGOUT VIEW
# ============================================================

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        ip = request.META.get("REMOTE_ADDR")

        get_redis().delete(f"user_session:{user.id}")
        get_redis().delete(f"ip_session:{ip}")

        language = get_language_from_path(request.path)

        return Response(
            {"detail": t("auth.logout_success", language)},
            status=status.HTTP_200_OK
        )
