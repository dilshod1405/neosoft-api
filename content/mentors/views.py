# content/mentors/views.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from content.models import Course, Lesson, Quiz, Question, Answer, Resource
from .serializers import MentorCourseSerializer, MentorLessonSerializer, MentorQuizSerializer, MentorQuestionSerializer, MentorAnswerSerializer, MentorResourceSerializer
from permissions.user_permissions import IsMentor, MentorOwnsObject
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from content.vdocipher.vdocipher_utils import obtain_upload_credentials, upload_poster_to_vdocipher
from rest_framework.parsers import MultiPartParser, FormParser
from authentication.models import CustomUser
from django.shortcuts import get_object_or_404


class MentorCourseListCreateView(generics.ListCreateAPIView):
    serializer_class = MentorCourseSerializer
    permission_classes = [IsMentor]

    def get_queryset(self):
        return Course.objects.filter(
            instructor__mentor=self.request.user.mentor_profile
        )

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user.mentor_profile.instructor_profile)




class MentorCourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = MentorCourseSerializer
    permission_classes = [IsMentor, MentorOwnsObject]

    def perform_destroy(self, instance):
        if instance.lessons.filter(video_id__isnull=False).exists():
            raise PermissionDenied("Video mavjudligi uchun kursni o'chirish mumkin emas !")

        super().perform_destroy(instance)





class MentorLessonCreateView(generics.CreateAPIView):
    serializer_class = MentorLessonSerializer
    permission_classes = [IsMentor]

    def perform_create(self, serializer):
        course_id = self.kwargs["course_id"]
        course = Course.objects.get(id=course_id)

        if course.instructor.mentor != self.request.user.mentor_profile:
            raise PermissionDenied("Boshqa mentorlar .")

        serializer.save(course=course)




class MentorLessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.select_related("course", "course__instructor")
    serializer_class = MentorLessonSerializer
    permission_classes = [IsMentor, MentorOwnsObject]

    def perform_destroy(self, instance):
        if instance.video_id:
            raise PermissionDenied("Video mavjudligi uchun darsni o'chirish mumkin emas !")

        super().perform_destroy(instance)




class MentorInitiateUploadView(APIView):
    permission_classes = [IsMentor]

    def post(self, request, lesson_id):
        lesson = Lesson.objects.get(id=lesson_id)

        if lesson.course.instructor.mentor != request.user.mentor_profile:
            return Response({"error": "Access denied"}, status=403)

        creds = obtain_upload_credentials(
            folder_id=lesson.folder_id,
            title=lesson.title_uz
        )

        lesson.video_id = creds.get("videoId")
        lesson.vdocipher_status = "queued"
        lesson.save(update_fields=["video_id", "vdocipher_status"])

        return Response({
            "upload_url": creds["uploadUrl"],
            "clientPayload": creds["clientPayload"],
            "video_id": lesson.video_id
        })




class MentorPosterUploadView(APIView):
    permission_classes = [IsMentor, MentorOwnsObject]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, lesson_id):
        lesson = Lesson.objects.get(id=lesson_id)

        if "poster" not in request.data:
            return Response({"error": "Poster file is required"}, status=400)

        file = request.data["poster"]

        if not lesson.video_id:
            return Response({"error": "Lesson has no video yet"}, status=400)

        # Upload to VdoCipher
        try:
            result = upload_poster_to_vdocipher(lesson.video_id, file)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "message": "Poster updated successfully",
            "vdocipher_response": result
        })
    


class MentorQuizCreateView(generics.CreateAPIView):
    serializer_class = MentorQuizSerializer
    permission_classes = [IsMentor]

    def perform_create(self, serializer):
        lesson = Lesson.objects.get(id=self.kwargs["lesson_id"])

        if lesson.course.instructor.mentor != self.request.user.mentor_profile:
            raise PermissionDenied()

        serializer.save(lesson=lesson)




class MentorQuestionCreateView(generics.CreateAPIView):
    serializer_class = MentorQuestionSerializer
    permission_classes = [IsMentor]

    def perform_create(self, serializer):
        quiz = Quiz.objects.get(id=self.kwargs["quiz_id"])

        if quiz.lesson.course.instructor.mentor != self.request.user.mentor_profile:
            raise PermissionDenied()

        serializer.save(quiz=quiz)



class MentorQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.select_related(
        "quiz__lesson__course__instructor"
    )
    serializer_class = MentorQuestionSerializer
    permission_classes = [IsMentor, MentorOwnsObject]




class MentorQuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.select_related("lesson__course__instructor")
    serializer_class = MentorQuizSerializer
    permission_classes = [IsMentor, MentorOwnsObject]



class MentorAnswerCreateView(generics.CreateAPIView):
    serializer_class = MentorAnswerSerializer
    permission_classes = [IsMentor]

    def perform_create(self, serializer):
        question = Question.objects.get(id=self.kwargs["question_id"])

        if question.quiz.lesson.course.instructor.mentor != self.request.user.mentor_profile:
            raise PermissionDenied()

        serializer.save(question=question)



class MentorAnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.select_related(
        "question__quiz__lesson__course__instructor"
    )
    serializer_class = MentorAnswerSerializer
    permission_classes = [IsMentor, MentorOwnsObject]




class MentorResourceCreateView(generics.CreateAPIView):
    serializer_class = MentorResourceSerializer
    permission_classes = [IsMentor]

    def perform_create(self, serializer):
        lesson = Lesson.objects.get(id=self.kwargs["lesson_id"])

        if lesson.course.instructor.mentor != self.request.user.mentor_profile:
            raise PermissionDenied()

        serializer.save(lesson=lesson)



class MentorResourceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.select_related("lesson__course__instructor")
    serializer_class = MentorResourceSerializer
    permission_classes = [IsMentor, MentorOwnsObject]





class ChatCourseStudentsView(APIView):
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request, course_id):
        user = request.user
        mentor_profile = user.mentor_profile

        course = get_object_or_404(Course, id=course_id)

        if course.instructor.mentor != mentor_profile:
            return Response({"error": "Access denied"}, status=403)

        students = CustomUser.objects.filter(
            enrollments__course=course,
            enrollments__is_active=True,
            is_mentor=False
        ).distinct()

        data = [
            {
                "id": s.id,
                "full_name": s.full_name,
                "email": s.email
            }
            for s in students
        ]

        return Response(data)