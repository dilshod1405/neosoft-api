
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver
from content.models import Course
from discount.models import Discount


def update_discount_price(course: Course):
    valid_discounts = [d for d in course.discounts.all() if d.is_valid()]
    if valid_discounts:
        best_discount = max(valid_discounts, key=lambda d: d.value)
        course.discount_price = best_discount.calculate_discounted_price(course.price)
    else:
        course.discount_price = None
    course.save(update_fields=["discount_price"])


@receiver(m2m_changed, sender=Course.discounts.through)
def course_discounts_changed(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:
        update_discount_price(instance)


@receiver(post_save, sender=Discount)
def discount_saved(sender, instance, **kwargs):
    for course in instance.courses.all():
        update_discount_price(course)


@receiver(post_delete, sender=Discount)
def discount_deleted(sender, instance, **kwargs):
    for course in instance.courses.all():
        update_discount_price(course)


@receiver(post_save, sender=Course)
def course_price_changed(sender, instance, **kwargs):
    if "update_fields" in kwargs and kwargs["update_fields"] and "price" not in kwargs["update_fields"]:
        return
    update_discount_price(instance)