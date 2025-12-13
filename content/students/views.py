from rest_framework import generics, permissions
from content.models import Course, Question, Category
from permissions.user_permissions import IsCourseAccessible
from filters.course_filter import CourseFilter
from .serializers import StudentCourseSerializer, SubmitAnswerSerializer, CategoryChildSerializer
from django_filters.rest_framework import DjangoFilterBackend


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

    def get_serializer_context(self):
        return {"request": self.request}



class StudentCourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_published=True).select_related("category", "instructor")
    serializer_class = StudentCourseSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

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