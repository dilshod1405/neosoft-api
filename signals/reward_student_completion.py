from django.db.models.signals import post_save
from django.dispatch import receiver
from content.models import UserProgress
from discount.models import Discount
from content.students.models import CompletionPromoCode



@receiver(post_save, sender=UserProgress)
def reward_promo_on_completion(sender, instance, **kwargs):
    enrollment = instance.enrollment
    student = enrollment.student

    if enrollment.completion_percentage >= 90:
        if not CompletionPromoCode.objects.filter(student=student, discount__source='PROMO').exists():
            default_discount = Discount.objects.filter(source='PROMO', is_active=True).first()
            if default_discount:
                CompletionPromoCode.objects.create(student=student, discount=default_discount)