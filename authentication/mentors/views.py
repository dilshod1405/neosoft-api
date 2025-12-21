import os
from rest_framework.views import APIView
from rest_framework import viewsets, decorators
from rest_framework.response import Response
from permissions.user_permissions import IsMentor, IsOwner
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import MentorProfile, MentorContract
from .serializers import InstructorProfileSerializer, MentorSecretProfileSerializer, MentorFullProfileSerializer
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

        passport_number = request.data.get("passport_number")
        if passport_number and MentorProfile.objects.filter(passport_number=passport_number).exists():
            return Response({
                "detail": "Bu pasport raqami bilan mentor allaqachon mavjud."
            }, status=400)

        mentor_profile, _ = MentorProfile.objects.get_or_create(user=user)

        instructor_profile, _ = InstructorProfile.objects.get_or_create(mentor=mentor_profile)

        instructor_ser = InstructorProfileSerializer(
            instructor_profile,
            data=request.data,
            partial=True
        )

        mentor_ser = MentorSecretProfileSerializer(
            mentor_profile,
            data=request.data,
            partial=True
        )

        if instructor_ser.is_valid() and mentor_ser.is_valid():

            instructor_ser.save()
            mentor_ser.save()
            user.is_mentor = True
            user.save(update_fields=["is_mentor"])

            return Response({
                "detail": "Tabriklaymiz! Siz endi mentorsiz. Ammo, balans ochilishi uchun shartnomani imzolang."
            }, status=201)

        return Response({
            "instructor_errors": instructor_ser.errors,
            "secret_errors": mentor_ser.errors,
        }, status=400)




# =====================================================================
#                    MENTOR PROFILE CRUD VIEW
# =====================================================================

class MentorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = MentorFullProfileSerializer
    permission_classes = [IsAuthenticated, IsMentor, IsOwner]

    def get_queryset(self):
        return MentorProfile.objects.filter(user=self.request.user)

    def get_object(self):
        return MentorProfile.objects.get(user=self.request.user)

    @decorators.action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        profile = self.get_object()

        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        serializer = self.get_serializer(profile, data=request.data, partial=(request.method == "PATCH"))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)





# =====================================================================
#                    DOWNLOADING SECURED CONTRACT
# =====================================================================


class ContractDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        user = request.user

        if not getattr(user, "is_mentor", False):
            return Response({"detail": "Siz mentor emassiz"}, status=403)

        try:
            mentor_profile = user.mentor_profile
            contract = mentor_profile.contract
        except MentorContract.DoesNotExist:
            raise Http404("Shartnoma topilmadi")

        if not contract.pdf_file or not contract.pdf_file.name:
            raise Http404("PDF fayl yuklanmagan")

        file_path = os.path.join(
            settings.PRIVATE_CONTRACT_ROOT,
            contract.pdf_file.name
        )

        if not os.path.exists(file_path):
            raise Http404("PDF fayl mavjud emas")

        user_obj = contract.mentor.user

        if hasattr(user_obj, "get_full_name") and isinstance(user_obj.get_full_name, str):
            full_name = user_obj.get_full_name
        else:
            full_name = f"{user_obj.first_name} {user_obj.last_name}".strip()

        if not full_name:
            full_name = f"user_{user_obj.id}"

        nice_filename = f"Shartnoma_{full_name}.pdf"

        response = FileResponse(
            open(file_path, "rb"),
            as_attachment=True,
            filename=nice_filename
        )
        response["Content-Type"] = "application/pdf"
        return response