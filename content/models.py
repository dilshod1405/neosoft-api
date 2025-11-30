from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from content.mentors.models import InstructorProfile
from authentication.models import CustomUser
from django.utils.translation import get_language
from discount.models import Discount


User = CustomUser

# ============================================================
#                  SPECIALITY INFO
# ============================================================

class Category(models.Model):
    name_uz = models.CharField(max_length=100, unique=True)
    name_ru = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    folder_id = models.CharField(max_length=100, blank=True, null=True, help_text="VdoCipher folder ID (for category/subcategory)")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_uz)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_uz

    @property
    def safe_name(self):
        return self.name_uz or self.name_ru or "Unnamed"




# ==================================================================
#                  COURSE INFO (RELATED TO SPECIALITY)
# ==================================================================

class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    ]

    title_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description_uz = models.TextField()
    description_ru = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE, related_name='courses_taught')
    price = models.IntegerField(validators=[MinValueValidator(0)], default=0.00)
    discount_price = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    duration_hours = models.PositiveIntegerField(default=0)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)  # Reference LEVEL_CHOICES
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='dependent_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    discounts = models.ManyToManyField(Discount, blank=True, related_name='courses')
    is_bestseller = models.BooleanField(default=False)
    folder_id = models.CharField(max_length=100, blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_uz)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.title_uz} - {self.instructor}'

    @property
    def safe_title(self):
        return self.title_uz or self.title_ru or "Untitled"






# ==================================================================
#                      STUDENT LEARNING PROGRESS
# ==================================================================

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments', limit_choices_to={'is_mentor': False})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    completion_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])

    class Meta:
        unique_together = ('student', 'course')

    def recalculate_completion(self):
        total_weight = sum(lesson.weight for lesson in self.course.lessons.all())
        if total_weight == 0:
            self.completion_percentage = 0
        else:
            completed_weight = sum(
                up.lesson.weight for up in self.progress.filter(completed_at__isnull=False).select_related('lesson')
            )
            video_progress = (completed_weight / total_weight)

            quiz_avg = self.progress.filter(quiz_score__isnull=False).aggregate(avg=models.Avg('quiz_score'))['avg'] or 0
            quiz_progress = (quiz_avg / 100) * 30

            self.completion_percentage = int(video_progress + quiz_progress)

        self.save(update_fields=["completion_percentage"])

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title_uz}"

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title_uz}"





# ==================================================================
#                    LESSON INFO (RELATED TO COURSE)
# ==================================================================

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    content_uz = models.TextField()
    content_ru = models.TextField()
    video_id = models.CharField(max_length=100, blank=True, null=True, help_text="vdocipher.com video ID for secure playback")
    folder_id = models.CharField(max_length=100, blank=True, null=True, help_text="VdoCipher folder ID")
    order = models.PositiveIntegerField(default=0)
    weight = models.PositiveIntegerField(default=1, help_text="Lesson weight for progress calculation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_preview = models.BooleanField(default=False)
    vdocipher_payload = models.JSONField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection, if applicable")
    vdocipher_status = models.CharField(
        max_length=20,
        choices=[('pre-upload', 'Pre-Upload'), ('queued', 'Queued'), ('ready', 'Ready'), ('failed', 'Failed')],
        default='pre-upload'
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.title_uz} (Course: {self.course.title_uz})"





# ==================================================================
#                         QUIZES FOR LESSON
# ==================================================================

class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title_uz = models.CharField(max_length=200)
    title_ru = models.CharField(max_length=200)
    passing_score = models.PositiveIntegerField(default=70, validators=[MaxValueValidator(100)])

    def __str__(self):
        return f"{self.title_uz} (Lesson: {self.lesson.title_uz})"
    




# ==================================================================
#                         QUESTION FOR LESSON
# ==================================================================

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text_uz = models.TextField()
    text_ru = models.TextField()
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.text_uz[:50]}..."
    




# ==================================================================
#                         ANSWER FOR QUESTION
# ==================================================================

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text_uz = models.CharField(max_length=200)
    text_ru = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text_uz
    




# ==================================================================
#                      COURSE RATING FOR LESSON
# ==================================================================

class CourseRating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings', limit_choices_to={'is_mentor': False})
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_uz = models.TextField(blank=True)
    review_ru = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'user')

    def __str__(self):
        return f"{self.user.full_name} rated {self.course.title_uz} - {self.rating}/5"

    @property
    def safe_review(self):
        lang = get_language()

        if lang == "uz" and self.review_uz:
            return self.review_uz
        if lang == "ru" and self.review_ru:
            return self.review_ru

        return self.review_uz or self.review_ru or ""





# ==================================================================
#                      RESOURCE FOR LESSON
# ==================================================================

class Resource(models.Model):
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(max_length=200)
    file = models.FileField(
        upload_to='lesson_resources/',
        help_text="PDF, DOCX, PPTX, ZIP va boshqa materiallar"
    )
    file_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Masalan: pdf, docx, pptx, zip"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.lesson.title_uz})"

    def save(self, *args, **kwargs):
        # Fayl turini avtomatik aniqlash
        if self.file and not self.file_type:
            self.file_type = self.file.name.split('.')[-1].lower()
        super().save(*args, **kwargs)





# ==================================================================
#                    USER PROGRESS ACCROSS COURSE
# ==================================================================

class UserProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    completed_at = models.DateTimeField(null=True, blank=True)
    quiz_score = models.PositiveIntegerField(null=True, blank=True, validators=[MaxValueValidator(100)])

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"{self.enrollment.student.full_name} - {self.lesson.title_uz}"