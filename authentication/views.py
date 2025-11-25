from .models import CustomUser
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import RegisterUserSerializer
from emails.auth.registration_code_email import registration_code_email
User = CustomUser

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):

        # Detect language
        language = 'uz'
        if '/ru/' in request.path:
            language = 'ru'

        # is_verified user oldin ro‘yxatdan o‘tganmi?
        existing_verified = User.objects.filter(
            email=request.data.get("email"),
            is_verified=True
        ).first()

        if existing_verified:
            return Response({
                "detail": "This email is already registered and verified."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        validated_data['is_active'] = False

        user = User.objects.create_user(**validated_data)


        # Send activation email
        registration_code_email.delay(user.id, language)
        logger.info(f"Activation code sent to {user.email} for language {language}")

        return Response({
            'message': 'User registered successfully. Please check your email for activation code.',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
