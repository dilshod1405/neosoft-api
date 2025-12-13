from django.urls import path
from .views import StudentProfileMeView

urlpatterns = [
    path("profile/me/", StudentProfileMeView.as_view(), name="student-profile-me"),
]
