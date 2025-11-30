from notification.models import Notification
from django.utils import timezone

def send_notification_to_user(user, title, message):
    if user is None:
        return None

    return Notification.objects.create(
        user=user,
        title=title,
        message=message
    )


def remove_expired_notifications():
    now = timezone.now()
    Notification.objects.filter(valid_until__lt=now).delete()