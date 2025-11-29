from django.db import models
from django.utils import timezone
from utils.generator_promo_code import generate_promo_code



class CompletionPromoCode(models.Model):
    student = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='promo_codes')
    code = models.CharField(max_length=20, unique=True)
    discount = models.ForeignKey('discounts.Discount', on_delete=models.CASCADE, related_name='completion_codes')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    @property
    def is_valid(self):
        return not self.is_used and self.discount.is_valid()

    def save(self, *args, **kwargs):
        if not self.code:
            unique = False
            while not unique:
                code = generate_promo_code()
                if not CompletionPromoCode.objects.filter(code=code).exists():
                    unique = True
                    self.code = code
        super().save(*args, **kwargs)

    def mark_used(self):
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_at'])

    def __str__(self):
        return f"{self.student.full_name} — {self.code}"
