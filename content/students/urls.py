from django.urls import path
from .views import StudentCourseDetailView, StudentCourseListView, SubmitAnswerView

urlpatterns = [
    path("student/courses/", StudentCourseListView.as_view(), name="student-course-list"),
    path("student/courses/<slug:slug>/", StudentCourseDetailView.as_view(), name="student-course-detail"),
    path("student/questions/<int:question_id>/answer/", SubmitAnswerView.as_view(), name="submit-answer")
]
