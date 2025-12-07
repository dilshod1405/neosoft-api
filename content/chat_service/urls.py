from django.urls import path
from .views import ChatLessonDetailView, ChatCheckAccessView, ChatUserDetailView

urlpatterns = [
    path("lesson/<int:pk>/detail/", ChatLessonDetailView.as_view()),
    path("check-access/", ChatCheckAccessView.as_view()),
    path("users/<int:pk>/", ChatUserDetailView.as_view()),

]
