# payment/models.py
from django.db import models
from django.conf import settings
from decimal import Decimal

from discount.models import Discount
from content.models import Course, Enrollment

User = settings.AUTH_USER_MODEL


# ==================================================================
#                       ORDERS, CREATED BY USERS
# ==================================================================

class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="orders")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, blank=True, null=True)
    final_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.id} - {self.student}"

    @classmethod
    def create_with_final_price(cls, student, course, discount=None):
        if discount and getattr(discount, "is_valid", lambda: False)():
            price = Decimal(discount.calculate_discounted_price(course.price))
        else:
            price = Decimal(course.discount_price or course.price)
        return cls.objects.create(
            student=student,
            course=course,
            discount=discount,
            final_price=price.quantize(Decimal("0.01")),
        )


# ==================================================================
#                 TRANSACTIONS INFO FOR PAYMENTS
# ==================================================================

class Transaction(models.Model):
    provider = models.CharField(max_length=50)  # payme, click, uzum, paynet
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    # store amounts as integer tiyin (1 so'm = 100 tiyin)
    amount = models.IntegerField()
    status = models.CharField(max_length=20, default="PENDING")
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    mentor_share = models.IntegerField(null=True, blank=True)
    platform_share = models.IntegerField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True, default=dict)
    perform_time = models.DateTimeField(null=True, blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)
    cancel_reason = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"Transaction {self.id} - {self.provider} - {self.status}"

    @classmethod
    def create_from_order(cls, order, provider, transaction_id=None, amount_tiyin=None):
        if amount_tiyin is None:
            amount_tiyin = order.final_price

        return cls.objects.create(
            order=order,
            provider=provider,
            transaction_id=transaction_id,
            amount=amount_tiyin,
            status="CREATED",
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        status_mapping = {
            "PENDING": "PENDING",
            "SUCCESS": "PAID",
            "CREATED": "PENDING",
            "CANCELLED": "CANCELLED",
            "FAILED": "CANCELLED",
        }
        new_order_status = status_mapping.get(self.status, "PENDING")
        if self.order.status != new_order_status:
            self.order.status = new_order_status
            self.order.save(update_fields=["status"])
