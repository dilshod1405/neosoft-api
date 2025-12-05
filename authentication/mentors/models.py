from django.db import models
from authentication.models import CustomUser
from django.core.files.storage import FileSystemStorage
from django.conf import settings


# ============================================================
#                  Mentor Detail Info
# ============================================================

class MentorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="mentor_profile")
    passport_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    passport_issued_by = models.CharField(max_length=255, blank=True)
    passport_issue_date = models.DateField(null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    card_number = models.CharField(max_length=20, blank=True)
    pinfl = models.CharField(max_length=14, blank=True, null=True)
    dob = models.DateField(null=True, blank=True, verbose_name='Birth Date')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentor: {self.user.first_name} {self.user.last_name}"


    def update_courses(self):
        self.total_courses = self.user.courses_as_mentor.count()
        self.save()





# ============================================================
#                  Mentor Contract Info
# ============================================================


private_contract_storage = FileSystemStorage(
    location=settings.PRIVATE_CONTRACT_ROOT,
    base_url=settings.PRIVATE_CONTRACT_URL,
)

class MentorContract(models.Model):
    mentor = models.OneToOneField(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name="contract"
    )

    pdf_file = models.FileField(null=True, blank=True, upload_to="", storage=private_contract_storage)

    document_id = models.CharField(max_length=64, null=True, blank=True)
    short_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=0)

    sent_at = models.DateTimeField(null=True, blank=True)
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract for {self.mentor.user.first_name} {self.mentor.user.last_name}"

