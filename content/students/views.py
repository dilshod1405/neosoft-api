from rest_framework import generics, permissions
from content.models import Course, Question, Category, Lesson, Enrollment
from permissions.user_permissions import IsCourseAccessible
from filters.course_filter import CourseFilter
from .serializers import StudentCourseSerializer, SubmitAnswerSerializer, CategoryChildSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from content.vdocipher.vdocipher_utils import (
    generate_otp, API_BASE, API_KEY
)
from utils.get_client_ip import get_client_ip
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
import json
import requests
import ipaddress
from rest_framework.response import Response



class StudentCourseListView(generics.ListAPIView):
    queryset = (
        Course.objects
        .filter(is_published=True)
        .select_related("category", "instructor")
        .prefetch_related("lessons")
    )
    serializer_class = StudentCourseSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CourseFilter
    authentication_classes = [
        JWTAuthentication,
        SessionAuthentication,
    ]

    def get_serializer_context(self):
        return {"request": self.request}



class StudentCourseDetailView(generics.RetrieveAPIView):
    queryset = (
        Course.objects
        .filter(is_published=True)
        .select_related("category", "instructor")
        .prefetch_related(
            "lessons",
            "lessons__quizzes",
            "lessons__quizzes__questions",
            "lessons__quizzes__questions__answers",
            "lessons__resources",
        )
    )
    serializer_class = StudentCourseSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    def get_serializer_context(self):
        return {"request": self.request}






class SubmitAnswerView(generics.CreateAPIView):
    serializer_class = SubmitAnswerSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseAccessible]
    queryset = Question.objects.all()





class StudentCategoryTreeView(generics.ListAPIView):
    serializer_class = CategoryChildSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Return only root categories (no parent)
        return Category.objects.filter(parent__isnull=True).prefetch_related("subcategories")





class VdoCipherOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, video_id):
        lesson = get_object_or_404(Lesson, video_id=video_id)

        if not Enrollment.objects.filter(
            student=request.user,
            course=lesson.course,
            is_active=True
        ).exists():
            return Response({"error": "You don't have access to this video"}, status=403)

        client_ip = get_client_ip(request)

        user_id = f"user_{request.user.id}"

        annotate_string = json.dumps([{
            "type": "rtext",
            "text": request.user.email,
            "alpha": "0.60",
            "color": "0xFFFFFF",
            "size": "15",
            "interval": "5000"
        }])

        payload = {
            "ttl": 300,
            "annotate": annotate_string,
            "userId": user_id,
            "whitelisthref": "edu.neosoft.uz",
        }

        if client_ip:
            try:
                ip_obj = ipaddress.ip_address(client_ip)
                if ip_obj.version == 4 and not ip_obj.is_private:
                    payload["ipGeo"] = {"allow": [client_ip]}
            except ValueError:
                pass

        url = f"{API_BASE}/videos/{video_id}/otp"

        try:
            response = requests.post(
                url,
                headers={
                    "Authorization": f"Apisecret {API_KEY}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10,
            )

            if response.status_code not in (200, 201):
                return Response(
                    {"error": "Failed to generate OTP", "vdocipher_msg": response.text},
                    status=response.status_code
                )

            otp_data = response.json()
            otp_data["client_ip"] = client_ip
            return Response(otp_data)

        except Exception as e:
            return Response(
                {"error": "Vdocipher connection failed", "details": str(e)},
                status=502
            )
