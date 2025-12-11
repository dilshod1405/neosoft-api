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
User = CustomUser

import logging
logger = logging.getLogger(__name__)



# ============================================================
#                  REGISTRAION USER VIEW
# ============================================================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):

        language = 'uz'
        if '/ru/' in request.path:
            language = 'ru'

        existing_verified = User.objects.filter(
            email=request.data.get("email"),
            is_verified=True
        ).first()

        if existing_verified:
            return Response({
                "detail": "Bu email allaqachon ro'yhatdan o'tgan va tasdiqlangan."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data['is_active'] = False

        user = User.objects.create_user(**validated_data)


        # Send activation email
        activation_code_email.delay(user.id, language)
        logger.info(f"Activation code sent to {user.email} for language {language}")

        return Response({
            'message': "Muvaffaqiyatli ro'yxatdan o'tdingiz. Profilni aktivlashtirish uchun elektron pochtangizga kod yubordik.",
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)




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
        return Response(serializer.validated_data)




# ============================================================
#                  REFRESH TOKEN VIEW
# ============================================================

class RefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 200 and hasattr(response.data, "get"):
            refresh_token = response.data.get("refresh")
            access_token = response.data.get("access")
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token_obj = RefreshToken(refresh_token)
                jti = token_obj["jti"]
                user_id = token_obj["user_id"]

                ip = request.META.get("REMOTE_ADDR")
                session = get_redis().get(f"user_session:{user_id}")
                print("=== REFRESH DEBUG ===")
                print("REFRESH JTI:", jti)
                print("REDIS:", get_redis().get(f"user_session:{user_id}"))
                print("IP:", ip)

                if session:
                    old_jti, old_ip = session.split(":")
                    if old_ip != ip or old_jti != jti:
                        response.data = {"detail": "Qurilma ishi to'xtatildi — yangi qurilmadan kirish aniqlandi."}
                        response.status_code = 401
                        return super().finalize_response(request, response, *args, **kwargs)

                    ttl = 7 * 24 * 60 * 60
                    get_redis().setex(f"user_session:{user_id}", ttl, f"{jti}:{ip}")
                    get_redis().setex(f"ip_session:{ip}", ttl, f"{user_id}:{jti}")

        return super().finalize_response(request, response, *args, **kwargs)
    





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
        language = "ru" if "/ru/" in request.path else "uz"

        email = request.data.get("email")
        code = request.data.get("code")

        if not email or not code:
            return Response(
                {"error": "Email and code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email, is_verified=False)

            stored_code = get_stored_code(user.id)

            # === CODE CHECK ===
            if stored_code and stored_code == code:
                user.is_verified = True
                user.is_active = True
                user.save(update_fields=["is_verified", "is_active"])

                clear_stored_code(user.id)

                refresh = RefreshToken.for_user(user)
                access = str(refresh.access_token)

                return Response(
                    {
                        "message": f"Prfofil muvaffaqiyatli aktivlashtirildi. Xush kelibsiz, {user.last_name} {user.first_name} {user.middle_name} !",
                        "access": access,
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
                    },
                    status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Xato kod kiritildi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Foydalanuvchi topilmadi yoki allaqachon aktiv holatda."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": "Aktivatsiyada xatolik yuz berdi. Qayta urinib ko'ring."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# ============================================================
#                  RESEND ACTIVATION CODE VIEW
# ============================================================

class ResendCodeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ResendCodeSerializer

    def create(self, request, *args, **kwargs):
        language = "ru" if "/ru/" in request.path else "uz"

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = CustomUser.objects.get(email=email, is_verified=False)

            clear_stored_code(user.id)

            activation_code_email.delay(user.id, language)

            logger.info(f"New activation code sent to {user.email} ({language})")

            return Response(
                {
                    "success": True,
                    "message": "Yangi aktivlashtirish kodi elektron pochtangizga yuborildi."
                },
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            logger.warning(f"Resend code failed: user not found or already verified — {email}")
            return Response(
                {"error": "Foydalanuvchi topilmadi yoki allaqachon aktivlashtirilgan."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Resend activation code error: {str(e)}")
            return Response(
                {"error": "Kodni qayta yuborishda xatolik yuz berdi."},
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

        return Response({"detail": "Logged out"}, status=200)