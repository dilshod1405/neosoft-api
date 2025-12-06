from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django.utils.html import format_html
from django.urls import reverse



# ============================================================
#                  USER MANAGE ADMIN
# ============================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ["-date_joined"]
    list_display = ["email", "first_name", "last_name", "middle_name", "phone", "is_staff", "is_superuser", "is_verified", "is_mentor", "date_joined", "id"]
    list_filter = ["is_staff", "is_superuser", "is_verified", "is_active"]
    search_fields = ["email", "first_name", "last_name", "middle_name", "phone"]
    
    readonly_fields = ["date_joined"]

    fieldsets = (
        (_("Asosiy ma'lumotlar"), {
            "fields": ("email", "first_name", "last_name", "middle_name", "photo", "phone", "password")
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
            "fields": ("email", "first_name", "last_name", "middle_name", "phone", "password1", "password2", "is_staff", "is_superuser", "is_verified"),
        }),
    )

    list_display_links = ["email", "first_name"]
    list_editable = []
    list_per_page = 25  











# =========================================================================
#                    MENTOR & INSTRUCTOR ADMIN
# =========================================================================

from django.contrib import admin
from authentication.mentors.models import MentorContract, MentorProfile
from content.mentors.models import InstructorProfile


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
        "user__first_name",
        "user__last_name",
        "user__middle_name",
        "passport_number",
        "address",
        "dob",
        "pinfl",
        "passport_expiry_date",
        "card_number",
        "created_at",
        "id"
    ]

    search_fields = ["user__first_name", "user__last_name", "user__middle_name", "user__email", "passport_number", "card_number"]
    list_filter = ["created_at"]

    readonly_fields = ["created_at"]

    inlines = [MentorContractInline]

    fieldsets = (
        ("Mentor personal data", {
            "fields": (
                "user",
                "passport_number",
                "passport_issued_by",
                "passport_issue_date",
                "passport_expiry_date",
                "dob",
                "pinfl",
                "address",
                "card_number",
            )
        }),
        ("System information", {
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
        "sent_at",
        "is_signed",
        "signed_at",
        "created_at",
        "download_link",   # <= pdf_file o'rniga
        "id"
    ]

    search_fields = [
        "mentor__user__first_name",
        "mentor__user__last_name",
        "mentor__user__middle_name",
        "mentor__passport_number",
        "document_id",
    ]

    list_filter = ["status", "sent_at", "signed_at", "created_at", "is_signed"]

    readonly_fields = ["created_at", "sent_at", "signed_at", "download_link"]

    fieldsets = (
        ("Contract data", {
            "fields": (
                "mentor",
                "download_link",
                "document_id",
                "short_url",
                "status",
                "is_signed"
            )
        }),
        ("Time stamps", {
            "fields": ("sent_at", "signed_at", "created_at")
        }),
    )

    def download_link(self, obj):
        if not obj.pdf_file:
            return "❌ Fayl yo'q"

        url = reverse("admin-download-contract", args=[obj.pk])

        return format_html(
            '<a class="button" href="{}" target="_blank">📄 Shartnomani yuklash</a>',
            url
        )


    download_link.short_description = "Contract File"

# ==========================
#     INSTRUCTOR ADMIN
# ==========================

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "get_user_full_name",
        "expertise",
        "created_at",
    ]

    search_fields = [
        "mentor__user__first_name",
        "mentor__user__last_name",
        "mentor__user__middle_name",
        "mentor__user__email",
        "expertise",
    ]

    list_filter = ["created_at"]

    readonly_fields = ["created_at"]

    fieldsets = (
        ("Instructor information", {
            "fields": (
                "mentor",
                "bio_uz",
                "bio_ru",
                "expertise",
                "qualifications_uz",
                "qualifications_ru",
                "profile_picture",
            )
        }),
        ("System information", {
            "fields": ("created_at",),
        }),
    )

    def get_user_full_name(self, obj):
        return f"{obj.mentor.user.first_name} {obj.mentor.user.last_name}"

    get_user_full_name.short_description = "Instructor"

