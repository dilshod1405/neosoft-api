from django.urls import path, include

urlpatterns = [
    path("", include("content.students.urls")),
    path("mentor/", include("content.mentors.urls"))
]
