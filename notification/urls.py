from django.urls import path
from .views import NotificationCreateView, NotificationListView, UnreadNotificationListView, NotificationMarkReadView

urlpatterns = [
    path("create/", NotificationCreateView.as_view()),


    path("list/", NotificationListView.as_view()),
    path("unread-list/", UnreadNotificationListView.as_view()),
    path("<int:notif_id>/read/", NotificationMarkReadView.as_view()),
]
