from google.oauth2 import id_token
from google.auth.transport import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from authentication.models import CustomUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("id_token")

        if not token:
            return Response({"error": "id_token required"}, status=400)

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = idinfo.get("email")
            full_name = idinfo.get("name")
            picture = idinfo.get("picture")
            email_verified = idinfo.get("email_verified", False)

        except Exception:
            return Response({"error": "Invalid Google token"}, status=400)

        if not email:
            return Response({"error": "Google email not found"}, status=400)

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name or "",
                "is_verified": email_verified,
            }
        )

        if not created:
            if full_name and user.full_name != full_name:
                user.full_name = full_name
            if email_verified and not user.is_verified:
                user.is_verified = True
            user.save(update_fields=["full_name", "is_verified"])

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "photo": picture,
                "phone": user.phone,
                "is_verified": user.is_verified
            }
        })
