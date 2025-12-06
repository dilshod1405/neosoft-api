# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from authentication.models import CustomUser
# from payment.mentors.models import MentorBalance

# @receiver(post_save, sender=CustomUser)
# def create_mentor_balance(sender, instance, created, **kwargs):
#     if created and instance.is_mentor:
#         MentorBalance.objects.get_or_create(mentor=instance)
