from django.contrib import admin
from django.utils.html import format_html
from .models import Discount, Event
from utils.generator_promo_code import generate_promo_code

# ============================
# EVENT ADMIN
# ============================

class DiscountInline(admin.TabularInline):
    model = Discount
    extra = 0
    fields = ("name", "source", "value", "is_active")
    readonly_fields = ("name", "source", "value", "is_active")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_active", "status_display")
    search_fields = ("name",)
    list_filter = ("is_active",)
    inlines = [DiscountInline]

    def status_display(self, obj):
        if obj.is_valid():
            return format_html("<span style='color: green;'>Active</span>")
        return format_html("<span style='color: red;'>Expired</span>")
    status_display.short_description = "Status"


# ============================
# DISCOUNT ADMIN
# ============================

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "source",
        "discount_type",
        "value",
        "promo_code",
        "completion_promo_display",
        "usage_display",
        "is_active",
        "valid_status_colored",
    )
    search_fields = ("name", "promo_code")
    list_filter = ("source", "discount_type", "is_active")
    autocomplete_fields = ("event",)

    readonly_fields = (
        "usage_display",
        "max_usage_display",
        "completion_promo_display",
        "valid_status_colored",
        "generate_code_button",
    )

    fieldsets = (
        ("👤 Asosiy ma’lumotlar", {
            "fields": ("name", "description", "source", "discount_type", "value")
        }),
        ("🏷 Promo Code", {
            "fields": (
                "promo_code",
                "completion_promo_display",
                "usage_display",
                "max_usage_display",
                "generate_code_button",
            )
        }),
        ("📅 Vaqt va Holat", {
            "fields": ("is_active", "start_date", "end_date", "event", "valid_status_colored")
        })
    )

    # ======================
    # VALID STATUS
    # ======================
    def valid_status_colored(self, obj):
        if obj.is_valid():
            return format_html("<span style='color:green;font-weight:bold;'>Valid</span>")
        return format_html("<span style='color:red;font-weight:bold;'>Not Valid</span>")
    valid_status_colored.short_description = "Status"

    # ======================
    # USAGE INFO
    # ======================
    def usage_display(self, obj):
        used = getattr(obj, "usage_count", 0)
        max_use = getattr(obj, "max_usage", 1)  # default 1
        return f"{used}/{max_use}"
    usage_display.short_description = "Usage"

    def max_usage_display(self, obj):
        return getattr(obj, "max_usage", 1)
    max_usage_display.short_description = "Max Usage"

    # ======================
    # COMPLETION PROMO
    # ======================
    def completion_promo_display(self, obj):
        return "Yes" if getattr(obj, "completion_promo", False) else "No"
    completion_promo_display.short_description = "Completion Promo"

    # ======================
    # PROMO CODE GENERATOR BUTTON
    # ======================
    def generate_code_button(self, obj):
        if obj.source == "PROMO":
            return format_html(
                f"<a class='button' href='/admin/discount/discount/{obj.id}/generate-code/'>Generate</a>"
            )
        return "-"
    generate_code_button.short_description = "Generate Promo Code"

    # ======================
    # CUSTOM URL FOR BUTTON
    # ======================
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:discount_id>/generate-code/",
                self.admin_site.admin_view(self.generate_new_code),
                name="discount-generate-code",
            )
        ]
        return custom_urls + urls

    def generate_new_code(self, request, discount_id):
        discount = Discount.objects.get(id=discount_id)
        discount.promo_code = generate_promo_code()
        discount.save()
        self.message_user(request, "Promo code updated successfully!")
        from django.shortcuts import redirect
        return redirect(f"/admin/discount/discount/{discount_id}/change/")
