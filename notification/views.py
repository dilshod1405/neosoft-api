from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from rest_framework import generics
from .models import Notification
from .serializers import NotificationCreateSerializer, NotificationSerializer
from .services import NotificationRealtimeService
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

User = get_user_model()


class NotificationCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        target = data["target"]

        if target == "mentor":
            users = User.objects.filter(is_mentor=True)
        elif target == "student":
            users = User.objects.filter(is_mentor=False)
        else:  # all
            users = User.objects.all()

        for user in users:
            notif = Notification.objects.create(
                user=user,
                type=data["type"],
                title=data["title"],
                message=data["message"],
                metadata=data.get("metadata", {}),
                action_url=data.get("action_url"),
                valid_until=data.get("valid_until"),
            )

            NotificationRealtimeService.send_realtime({
                "id": notif.id,
                "user_id": user.id,
                "type": notif.type,
                "title": notif.title,
                "message": notif.message,
                "metadata": notif.metadata,
                "action_url": notif.action_url,
                "created_at": notif.created_at.isoformat(),
            })

        return Response({"status": "Yaratildi"})






class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")





class UnreadNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user,
            is_read=False
        ).order_by("-created_at")





class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, notif_id):
        notif = get_object_or_404(Notification, id=notif_id, user=request.user)

        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=["is_read", "read_at"])

        return Response({"status": "read"}, status=status.HTTP_200_OK)