from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from content.models import Lesson, Enrollment
from .serializers import ChatLessonSerializer
from rest_framework.generics import RetrieveAPIView
from authentication.models import CustomUser
from .serializers import ChatUserSerializer
from rest_framework.permissions import IsAuthenticated



class ChatLessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.select_related(
        "course",
        "course__instructor",
        "course__instructor__mentor",
        "course__instructor__mentor__user",
    )
    serializer_class = ChatLessonSerializer
    permission_classes = [IsAuthenticated]





class ChatCheckAccessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        lesson_id = request.GET.get("lesson_id")
        student_id = request.GET.get("student_id")

        if not lesson_id or not student_id:
            return Response({"error": "lesson_id and student_id are required"}, status=400)

        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.course
        student = int(student_id)

        is_enrolled = Enrollment.objects.filter(
            student_id=student,
            course=course,
            is_active=True
        ).exists()

        if not is_enrolled:
            return Response({
                "allowed": False,
                "reason": "Student is not enrolled in this course."
            }, status=403)

        return Response({
            "allowed": True,
            "course_id": course.id,
            "teacher_id": course.instructor.mentor.id,
            "student_id": student
        })
    




class ChatUserDetailView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ChatUserSerializer
    permission_classes = [IsAuthenticated]