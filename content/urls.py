from django.urls import path, include
from content.vdocipher.vdocipher_views import vdocipher_webhook

urlpatterns = [
    path("student/", include("content.students.urls")),
    path("mentor/", include("content.mentors.urls")),
    path("webhooks/vdocipher/", vdocipher_webhook, name="vdocipher-webhook"),
]
