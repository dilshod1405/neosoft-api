from django.db import models
from authentication.models import CustomUser

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
    address = models.CharField(max_length=255, blank=True)
    card_number = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mentor Secret Profile: {self.user.full_name}"


    def update_courses(self):
        self.total_courses = self.user.courses_as_mentor.count()
        self.save()



class MentorContract(models.Model):
    mentor = models.OneToOneField(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name="contract"
    )

    pdf_file = models.FileField(upload_to="contracts/", null=True, blank=True)

    document_id = models.CharField(max_length=64, null=True, blank=True)
    short_url = models.CharField(max_length=255, null=True, blank=True)
    status = models.IntegerField(default=0)

    sent_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contract for {self.mentor.user.full_name}"