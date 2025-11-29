from django.db.models.signals import post_save
from django.dispatch import receiver
from content.models import UserProgress

# ==================================================================
#                UPDATE ENROLLMENT EVERY SAVED PROGRESS
# ==================================================================

@receiver(post_save, sender=UserProgress)
def update_enrollment_completion(sender, instance, **kwargs):
    instance.enrollment.recalculate_completion()
