from django.db import models
from authentication.models import CustomUser
from authentication.mentors.models import MentorProfile



# ==================================================================
#            CONNECTION BETWEEN MENTOR AND VDOCIPHER.COM
# ==================================================================

class MentorVideo(models.Model):
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='uploaded_videos')
    video_id = models.CharField(max_length=100, unique=True)
    folder_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or self.video_id} — {self.mentor.full_name}"





# ============================================================
#                  Mentor Bio for Students
# ============================================================

class InstructorProfile(models.Model):
    mentor = models.OneToOneField(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name="instructor_profile",
        null=True
    )

    bio_uz = models.TextField(max_length=500, blank=True)
    bio_ru = models.TextField(max_length=500, blank=True)

    expertise = models.CharField(max_length=200, blank=True)

    qualifications_uz = models.TextField(max_length=1000, blank=True)
    qualifications_ru = models.TextField(max_length=1000, blank=True)

    profile_picture = models.ImageField(upload_to='instructors/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Instructor Profile of {self.mentor.user.first_name} {self.mentor.user.last_name}"
