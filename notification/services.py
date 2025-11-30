from .models import Notification

def create_user_notification(user, title, message):
    return Notification.objects.create(
        user=user,
        title=title,
        message=message
    )