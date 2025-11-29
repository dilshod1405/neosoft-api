from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

# ==================================================
#       Event (holiday discounts, promotions)
# ==================================================

class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def is_valid(self) -> bool:
        now = timezone.now()
        return self.is_active and (self.end_date is None or self.end_date > now) and self.start_date <= now




# ==============================
#           Discount
# ==============================

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("PERCENTAGE", "Percentage"),
        ("FLAT", "Flat"),
    ]
    SOURCE_CHOICES = [
        ("PROMO", "Promo Code"),
        ("HOLIDAY", "Holiday Discount"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default="PERCENTAGE")
    value = models.IntegerField(validators=[MinValueValidator(1)])
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    promo_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, blank=True, null=True, related_name="discounts")

    def __str__(self):
        return f"{self.name} ({self.source})"

    def is_valid(self) -> bool:
        now = timezone.now()
        return (
            self.is_active
            and (self.end_date is None or self.end_date > now)
            and self.start_date <= now
            and (self.source != "HOLIDAY" or (self.event and self.event.is_valid()))
        )

    def calculate_discounted_price(self, original_price: Decimal) -> Decimal:
        if not self.is_valid():
            return original_price

        value = Decimal(self.value)

        if self.discount_type == "PERCENTAGE":
            discount = (original_price * value) / Decimal("100")
            return original_price - discount

        return original_price - value