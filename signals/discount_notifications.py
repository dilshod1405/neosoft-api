from django.db.models.signals import post_save
from django.dispatch import receiver
from discount.models import Discount
from utils.sender_notification import send_notification_to_user


@receiver(post_save, sender=Discount)
def notify_mentor_on_discount_created(sender, instance, created, **kwargs):
    if not created:
        return

    courses = instance.courses.all()

    for course in courses:
        mentor = getattr(course, "teacher", None)
        if mentor:
            send_notification_to_user(
                user=mentor,
                title="Yangi chegirma taklifi",
                message=f"'{course.title}' kursi uchun yangi chegirma yaratildi: {instance.name}. "
                        "Uni tasdiqlaysizmi?",
                valid_until=instance.end_date
            )
