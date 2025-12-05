import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import MentorProfile, MentorContract
from .serializers import InstructorProfileSerializer, MentorSecretProfileSerializer
from content.mentors.models import InstructorProfile
from django.http import FileResponse, Http404
from django.conf import settings



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




class ContractDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not user.is_mentor:
            return Response({"detail": "Siz mentor emassiz"}, status=403)

        try:
            contract = user.mentor_profile.contract
        except MentorContract.DoesNotExist:
            raise Http404("Shartnoma topilmadi")

        if not contract.pdf_file or not contract.pdf_file.name:
            raise Http404("PDF fayl yuklanmagan")

        file_path = os.path.join(settings.PRIVATE_CONTRACT_ROOT, contract.pdf_file.name)

        if not os.path.exists(file_path):
            raise Http404("PDF fayl mavjud emas")

        nice_filename = f"Shartnoma_{contract.mentor.user.get_full_name()}.pdf"

        response = FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=nice_filename
        )
        response["Content-Type"] = "application/pdf"
        return response