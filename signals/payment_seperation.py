from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import Transaction
from payment.mentors.models import MentorBalance, MentorBalanceHistory
from authentication.models import CustomUser

User = CustomUser

# ---------------- MentorBalance ----------------
@receiver(post_save, sender=User)
def create_mentor_balance(sender, instance, **kwargs):
    if getattr(instance, "is_mentor", False):
        MentorBalance.objects.get_or_create(mentor=instance)


# ---------------- Mentor va Platform ulushi ----------------
@receiver(post_save, sender=Transaction)
def distribute_shares(sender, instance, created, **kwargs):
    if instance.status == "SUCCESS" and instance.amount is not None:
        mentor_share = int(instance.amount * 0.8)
        platform_share = int(instance.amount * 0.2)
        Transaction.objects.filter(id=instance.id).update(
            mentor_share=mentor_share,
            platform_share=platform_share
        )

# ---------------- Mentor balansini yangilash ----------------
@receiver(post_save, sender=Transaction)
def update_mentor_balance_on_success(sender, instance: Transaction, created, **kwargs):
    if instance.status != "SUCCESS" or instance.amount is None:
        return

    order = instance.order
    course = order.course
    instructor_profile = getattr(course, "instructor", None)
    if not instructor_profile or not instructor_profile.user:
        return

    mentor = instructor_profile.user
    mentor_share = int(instance.amount * 0.8)

    balance, _ = MentorBalance.objects.get_or_create(mentor=mentor)
    balance.balance += mentor_share
    balance.save()

    MentorBalanceHistory.objects.create(
        mentor=mentor,
        amount=mentor_share,
        description=f"{course.title_uz} kursidan tushgan daromad"
    )
