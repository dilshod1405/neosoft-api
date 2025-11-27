from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser



# ============================================================
#                  USER MANAGE ADMIN
# ============================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ["-date_joined"]
    list_display = ["email", "full_name", "phone", "is_staff", "is_superuser", "is_verified", "is_mentor", "date_joined", "id"]
    list_filter = ["is_staff", "is_superuser", "is_verified", "is_active"]
    search_fields = ["email", "full_name", "phone"]
    
    readonly_fields = ["date_joined"]

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            "fields": ("email", "full_name", "photo", "phone", "password")
        }),
        (_("Statuslar"), {
            "fields": ("is_active", "is_staff", "is_superuser", "is_verified", "is_mentor")
        }),
        (_("Ruxsatlar"), {
            "fields": ("groups", "user_permissions"),
        }),
        (_("Tizim ma'lumotlari"), {
            "fields": ("date_joined",),
        }),
    )

    add_fieldsets = (
        (_("Yangi foydalanuvchi qo'shish"), {
            "classes": ("wide",),
            "fields": ("email", "full_name", "phone", "password1", "password2", "is_staff", "is_superuser", "is_verified"),
        }),
    )

    list_display_links = ["email", "full_name"]
    list_editable = []
    list_per_page = 25  











# =========================================================================
#                    MENTOR & INSTRUCTOR ADMIN
# =========================================================================

from django.contrib import admin
from authentication.mentors.models import MentorContract, MentorProfile, InstructorProfile


# ==========================
#   MENTOR CONTRACT INLINE
# ==========================

class MentorContractInline(admin.StackedInline):
    model = MentorContract
    extra = 0
    can_delete = False
    readonly_fields = ["created_at", "sent_at", "signed_at"]
    fieldsets = (
        ("Contract Information", {
            "fields": (
                "pdf_file",
                "document_id",
                "short_url",
                "status",
                "sent_at",
                "signed_at",
                "created_at",
            )
        }),
    )


# ==========================
#       MENTOR ADMIN
# ==========================

@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "passport_number",
        "address",
        "card_number",
        "created_at",
    ]

    search_fields = ["user__full_name", "user__email", "passport_number", "card_number"]
    list_filter = ["created_at"]

    readonly_fields = ["created_at"]

    inlines = [MentorContractInline]

    fieldsets = (
        ("MENTOR PERSONAL DATA", {
            "fields": (
                "user",
                "passport_number",
                "passport_issued_by",
                "passport_issue_date",
                "address",
                "card_number",
            )
        }),
        ("SYSTEM INFORMATION", {
            "fields": ("created_at",),
        }),
    )


# ==========================
#     MENTOR CONTRACT ADMIN
# ==========================

@admin.register(MentorContract)
class MentorContractAdmin(admin.ModelAdmin):
    list_display = [
        "mentor",
        "document_id",
        "status",
        "short_url",
        "sent_at",
        "signed_at",
        "created_at",
    ]

    search_fields = [
        "mentor__user__full_name",
        "mentor__passport_number",
        "document_id",
    ]

    list_filter = ["status", "sent_at", "signed_at", "created_at"]

    readonly_fields = ["created_at", "sent_at", "signed_at"]

    fieldsets = (
        ("CONTRACT DATA", {
            "fields": (
                "mentor",
                "pdf_file",
                "document_id",
                "short_url",
                "status",
            )
        }),
        ("TIMESTAMPS", {
            "fields": ("sent_at", "signed_at", "created_at")
        }),
    )


# ==========================
#     INSTRUCTOR ADMIN
# ==========================

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "expertise",
        "created_at",
    ]

    search_fields = ["user__full_name", "user__email", "expertise"]
    list_filter = ["created_at"]

    readonly_fields = ["created_at"]

    fieldsets = (
        ("INSTRUCTOR INFORMATION", {
            "fields": (
                "user",
                "bio_uz",
                "bio_ru",
                "expertise",
                "qualifications_uz",
                "qualifications_ru",
                "profile_picture",
            )
        }),
        ("SYSTEM INFORMATION", {
            "fields": ("created_at",),
        }),
    )
