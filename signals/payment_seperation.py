from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from payment.models import Transaction, PlatformBalance, PlatformBalanceHistory
from payment.mentors.models import MentorBalance, MentorBalanceHistory
from authentication.models import CustomUser
from decimal import Decimal

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
def update_mentor_balance_on_status_change(sender, instance: Transaction, created, **kwargs):
    if instance.amount is None:
        return

    order = instance.order
    course = order.course
    instructor_profile = getattr(course, "instructor", None)
    if not instructor_profile or not instructor_profile.user:
        return

    mentor = instructor_profile.user
    mentor_share = int(instance.amount * Decimal("0.8"))
    platform_share = int(instance.amount * Decimal("0.2"))

    balance, _ = MentorBalance.objects.get_or_create(mentor=mentor)

    if instance.status == "SUCCESS":
        balance.balance += mentor_share
        MentorBalanceHistory.objects.create(
            mentor=mentor,
            amount=mentor_share,
            description=f"{course.title_uz} kursidan tushgan daromad"
        )
    elif instance.status == "CANCELLED":
        balance.balance -= mentor_share
        MentorBalanceHistory.objects.create(
            mentor=mentor,
            amount=-mentor_share,
            description=f"{course.title_uz} kursi bekor qilindi, summa qaytarildi"
        )

    balance.save()




@receiver(post_migrate)
def create_platform_balance(sender, **kwargs):
    PlatformBalance.objects.get_or_create(id=1)



@receiver(post_save, sender=Transaction)
def update_platform_balance(sender, instance: Transaction, created, **kwargs):
    if instance.amount is None:
        return

    platform_share = int(Decimal(instance.amount) * Decimal("0.2"))
    balance, _ = PlatformBalance.objects.get_or_create(id=1)

    if instance.status == "SUCCESS":
        balance.balance += platform_share
        PlatformBalanceHistory.objects.create(
            amount=platform_share,
            description=f"{instance.order.course.title_uz} kursidan tushgan platforma ulushi"
        )

    elif instance.status == "CANCELLED":
        balance.balance -= platform_share
        PlatformBalanceHistory.objects.create(
            amount=-platform_share,
            description=f"{instance.order.course.title_uz} kursi bekor qilindi, platforma ulushi qaytarildi"
        )

    balance.save()