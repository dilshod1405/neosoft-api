from django.contrib import admin
from .models import (
    Category, Course, Lesson, Quiz, Question, Answer,
    Resource, Enrollment, UserProgress, CourseRating
)


# ============================================================
#                   INLINE CONFIGURATIONS
# ============================================================

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0
    readonly_fields = ("file_type",)
    fields = ("title", "file", "file_type")


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    ordering = ["order"]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0



# ============================================================
#                   CATEGORY ADMIN
# ============================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name_uz", "name_ru", "parent", "slug")
    search_fields = ("name_uz", "name_ru")
    prepopulated_fields = {"slug": ("name_uz",)}
    list_filter = ("parent",)
    ordering = ("name_uz",)



# ============================================================
#                   COURSE ADMIN
# ============================================================

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title_uz", "order", "weight", "is_preview", "status")
    ordering = ("order",)
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title_uz", "category", "instructor", 
        "price", "discount_price", "level", 
        "is_published", "is_bestseller", "created_at", "id"
    )
    list_filter = (
        "category", "level", "is_published",
        "is_bestseller", "created_at"
    )
    search_fields = ("title_uz", "title_ru", "description_uz", "description_ru")
    inlines = [LessonInline]
    autocomplete_fields = ("instructor", "category", "prerequisites", "discounts")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title_uz",)}
    ordering = ("-created_at",)



# ============================================================
#                   LESSON ADMIN
# ============================================================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        "title_uz", "course", "order", "weight",
        "status", "vdocipher_status", "is_preview"
    )
    list_filter = ("status", "vdocipher_status", "is_preview", "course")
    search_fields = ("title_uz", "title_ru")
    inlines = [ResourceInline, QuizInline]
    autocomplete_fields = ("course",)
    ordering = ("course", "order")



# ============================================================
#                   QUIZ ADMIN
# ============================================================

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title_uz", "lesson", "passing_score")
    search_fields = ("title_uz", "title_ru")
    list_filter = ("passing_score", "lesson")
    inlines = [QuestionInline]
    autocomplete_fields = ("lesson",)



# ============================================================
#                   QUESTION ADMIN
# ============================================================

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text_uz_short", "quiz", "order")
    search_fields = ("text_uz", "text_ru")
    list_filter = ("quiz",)
    inlines = [AnswerInline]
    autocomplete_fields = ("quiz",)
    ordering = ("quiz", "order")

    def text_uz_short(self, obj):
        return (obj.text_uz[:50] + "...") if len(obj.text_uz) > 50 else obj.text_uz



# ============================================================
#                   ANSWER ADMIN
# ============================================================

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("text_uz", "question", "is_correct")
    search_fields = ("text_uz", "text_ru")
    list_filter = ("is_correct", "question")
    autocomplete_fields = ("question",)



# ============================================================
#                   RESOURCE ADMIN
# ============================================================

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "file_type", "created_at")
    search_fields = ("title",)
    list_filter = ("file_type", "lesson")
    autocomplete_fields = ("lesson",)
    readonly_fields = ("file_type",)
    ordering = ("-created_at",)



# ============================================================
#                   ENROLLMENT ADMIN
# ============================================================

class ProgressInline(admin.TabularInline):
    model = UserProgress
    extra = 0
    fields = ("lesson", "completed_at", "quiz_score")
    autocomplete_fields = ("lesson",)
    readonly_fields = ()
    ordering = ("lesson__order",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "student", "course", 
        "completion_percentage", 
        "is_active", 
        "enrolled_at"
    )
    list_filter = (
        "is_active", 
        "enrolled_at", 
        "course"
    )
    search_fields = ("student__full_name", "course__title_uz")
    autocomplete_fields = ("student", "course")
    readonly_fields = ("enrolled_at",)
    inlines = [ProgressInline]
    ordering = ("-enrolled_at",)



# ============================================================
#                  USER PROGRESS ADMIN
# ============================================================

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment", "lesson", 
        "completed_at", "quiz_score"
    )
    list_filter = ("completed_at", "lesson")
    autocomplete_fields = ("enrollment", "lesson")
    search_fields = ("enrollment__student__full_name", "lesson__title_uz")
    ordering = ("-completed_at",)



# ============================================================
#                   COURSE RATING ADMIN
# ============================================================

@admin.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "rating", "created_at")
    search_fields = ("course__title_uz", "user__full_name")
    list_filter = ("rating", "created_at")
    autocomplete_fields = ("course", "user")
    ordering = ("-created_at",)
