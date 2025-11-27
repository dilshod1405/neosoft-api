from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MentorProfile, InstructorProfile
from .serializers import InstructorProfileSerializer, MentorSecretProfileSerializer



# =====================================================================
#                    MENTOR APPLY (APPLICATION) VIEW
# =====================================================================

class MentorApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.is_mentor:
            return Response({"detail": "Siz allaqachon mentorsiz"}, status=400)

        instructor, _ = InstructorProfile.objects.get_or_create(user=user)
        instr_ser = InstructorProfileSerializer(instructor, data=request.data, partial=True)

        passport_number = request.data.get("passport_number")
        if MentorProfile.objects.filter(passport_number=passport_number).exists():
            return Response({
                "detail": "Mentor profile with this passport number already exists."
            }, status=400)

        mentor = MentorProfile(user=user)
        secret_ser = MentorSecretProfileSerializer(mentor, data=request.data, partial=True)

        if instr_ser.is_valid() and secret_ser.is_valid():
            instr_ser.save()
            secret_ser.save()
            user.is_mentor = True
            user.save()

            return Response({"detail": "Tabriklaymiz! Siz endi mentorsiz"}, status=201)

        return Response({
            "instructor_errors": instr_ser.errors,
            "secret_errors": secret_ser.errors,
        }, status=400)