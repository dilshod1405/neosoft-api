from django.db.models.signals import post_save
from django.dispatch import receiver
from payment.models import Transaction, PlatformBalance, PlatformBalanceHistory
from payment.mentors.models import MentorBalance, MentorBalanceHistory, WithdrawRequest
from decimal import Decimal


@receiver(post_save, sender=Transaction)
def process_transaction_signal(sender, instance: Transaction, created, **kwargs):

    # Process only successful/cancelled states
    if instance.status not in ["SUCCESS", "CANCELLED"]:
        return

    order = instance.order
    course = order.course

    # instructor = InstructorProfile
    instructor_profile = getattr(course, "instructor", None)

    if not instructor_profile:
        return

    # FIX: InstructorProfile has no user → use instructor_profile.mentor.user
    mentor_user = getattr(instructor_profile.mentor, "user", None)

    if not mentor_user:
        return

    mentor_balance, _ = MentorBalance.objects.get_or_create(mentor=mentor_user)
    platform_balance, _ = PlatformBalance.objects.get_or_create(id=1)

    # 80/20 sharing
    mentor_share = int(Decimal(instance.amount) * Decimal("0.8"))
    platform_share = int(Decimal(instance.amount) * Decimal("0.2"))

    # =============================
    # SUCCESS CASE
    # =============================
    if instance.status == "SUCCESS":

        mentor_balance.balance += mentor_share
        mentor_balance.save()

        MentorBalanceHistory.objects.create(
            mentor=mentor_user,
            amount=mentor_share,
            description=f"Income from course: {course.title_uz}"
        )

        platform_balance.balance += platform_share
        platform_balance.save()

        PlatformBalanceHistory.objects.create(
            amount=platform_share,
            description=f"Platform revenue from course: {course.title_uz}"
        )

    # =============================
    # CANCELLED CASE (refund)
    # =============================
    elif instance.status == "CANCELLED":

        mentor_balance.balance -= mentor_share
        mentor_balance.save()

        MentorBalanceHistory.objects.create(
            mentor=mentor_user,
            amount=-mentor_share,
            description=f"Refund for course: {course.title_uz}"
        )

        platform_balance.balance -= platform_share
        platform_balance.save()

        PlatformBalanceHistory.objects.create(
            amount=-platform_share,
            description=f"Refund deducted from platform share for: {course.title_uz}"
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
                description=f"WithdrawRequest #{instance.id} approved"
            )
