from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import Transaction, PlatformBalance, PlatformBalanceHistory
from payment.mentors.models import MentorBalance, MentorBalanceHistory, WithdrawRequest
from decimal import Decimal


@receiver(post_save, sender=Transaction)
def process_transaction_signal(sender, instance: Transaction, created, **kwargs):

    if instance.status not in ["SUCCESS", "CANCELLED"]:
        return

    order = instance.order
    course = order.course
    instructor = getattr(course, "instructor", None)

    if not instructor or not instructor.user:
        return

    mentor = instructor.user
    mentor_balance, _ = MentorBalance.objects.get_or_create(mentor=mentor)
    platform_balance, _ = PlatformBalance.objects.get_or_create(id=1)

    mentor_share = int(Decimal(instance.amount) * Decimal("0.8"))
    platform_share = int(Decimal(instance.amount) * Decimal("0.2"))

    if instance.status == "SUCCESS":

        mentor_balance.balance += mentor_share
        mentor_balance.save()
        MentorBalanceHistory.objects.create(
            mentor=mentor,
            amount=mentor_share,
            description=f"{course.title_uz} kursi uchun daromad"
        )

        platform_balance.balance += platform_share
        platform_balance.save()
        PlatformBalanceHistory.objects.create(
            amount=platform_share,
            description=f"{course.title_uz} kursidan platformaga tushgan ulush"
        )

    elif instance.status == "CANCELLED":

        mentor_balance.balance -= mentor_share
        mentor_balance.save()
        MentorBalanceHistory.objects.create(
            mentor=mentor,
            amount=-mentor_share,
            description=f"{course.title_uz} qaytarildi, mentor ulushi minus qilindi"
        )

        platform_balance.balance -= platform_share
        platform_balance.save()
        PlatformBalanceHistory.objects.create(
            amount=-platform_share,
            description=f"{course.title_uz} qaytarildi, platforma ulushi minus qilindi"
        )





@receiver(post_save, sender=WithdrawRequest)
def update_mentor_balance(sender, instance, created, **kwargs):
    if not created and instance.status == "APPROVED":
        balance, _ = MentorBalance.objects.get_or_create(mentor=instance.mentor)
        if balance.balance >= instance.amount:
            balance.balance -= instance.amount
            balance.save()
            MentorBalanceHistory.objects.create(
                mentor=instance.mentor,
                amount=-instance.amount,
                description=f"WithdrawRequest #{instance.id} tasdiqlandi"
            )