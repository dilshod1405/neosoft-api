from django.urls import path
from .views import StudentCourseDetailView, StudentCourseListView, SubmitAnswerView, StudentCategoryTreeView

urlpatterns = [
    path("categories/", StudentCategoryTreeView.as_view(), name="student-category-tree"),
    path("courses/", StudentCourseListView.as_view(), name="student-course-list"),
    path("courses/<int:id>/", StudentCourseDetailView.as_view(), name="student-course-detail"),
    path("questions/<int:question_id>/answer/", SubmitAnswerView.as_view(), name="submit-answer")
]
