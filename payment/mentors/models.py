from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class MentorBalance(models.Model):
    mentor = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor_balance")
    balance = models.IntegerField(default=0)  # so'mda saqlanadi
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mentor.get_full_name()} - Balance: {self.balance} so'm"


class MentorBalanceHistory(models.Model):
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mentor_balance_history")
    amount = models.IntegerField()  # so'm
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.mentor} | +{self.amount} so'm | {self.created_at}"


class WithdrawRequest(models.Model):
    STATUS = (
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("PAID", "Paid"),
    )

    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="withdraw_requests")
    amount = models.IntegerField()  # so'm
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.mentor} | {self.amount} so'm | {self.status}"
