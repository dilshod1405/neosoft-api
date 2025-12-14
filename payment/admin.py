from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, Transaction, PlatformBalance, PlatformBalanceHistory
from payment.mentors.models import MentorBalance, MentorBalanceHistory, WithdrawRequest
from django.conf import settings
from payment.multicard.payout import mentor_create_payout
from django.contrib import messages
from authentication.mentors.models import MentorProfile




# ------------------ Transaction Form ------------------
class TransactionAdminForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        order = cleaned_data.get('order')
        amount = cleaned_data.get('amount')

        if order and (amount is None):
            cleaned_data['amount'] = order.final_price
        return cleaned_data
    




# ------------------ Transaction Inline ------------------
class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    can_delete = False
    show_change_link = True
    readonly_fields = (
        "provider",
        "transaction_id",
        "amount_som",
        "status",
        "created_at_display",
    )

    def amount_som(self, obj):
        return f"{(obj.amount or 0):,} so'm"

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else "-"
    created_at_display.short_description = "Created At"





# ------------------ Order Admin ------------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "get_course", "get_mentor", "get_discount", "final_price", "status", "created_at")
    list_filter = ("created_at", "status")
    search_fields = ("id", "student__username", "course__title_uz", "course__mentor__username")
    readonly_fields = ("final_price", "created_at", "status")
    inlines = [TransactionInline]
    ordering = ("-created_at",)

    def get_course(self, obj):
        return obj.course.title_uz if obj.course else "-"
    get_course.short_description = "Course"

    def get_mentor(self, obj):
        instructor = obj.course.instructor if obj.course else None

        if (
            instructor
            and instructor.mentor
            and instructor.mentor.user
        ):
            user = instructor.mentor.user
            return f"{user.first_name} {user.last_name}"

        return "-"


    def get_discount(self, obj):
        return obj.discount.name if obj.discount else "-"
    get_discount.short_description = "Discount"





# ------------------ Transaction Admin ------------------
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    list_display = ("id", "order_link", "provider", "transaction_id", "amount_som",
                    "mentor_share_som", "platform_share_som", "status", "created_at_display")
    list_filter = ("provider", "status", "created_at")
    search_fields = ("transaction_id", "order__id", "order__student__username")

    readonly_fields = ("provider", "transaction_id", "amount", "amount_som",
                       "mentor_share_som", "platform_share_som", "status", "created_at_display")

    def order_link(self, obj):
        if obj.order:
            url = f"/admin/payment/order/{obj.order.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.order.id)
        return "-"
    order_link.short_description = "Order"

    def amount_som(self, obj):
        return f"{(obj.amount or 0):,} so'm"

    def mentor_share_som(self, obj):
        if not obj.amount:
            return "-"
        share = int(obj.amount * 0.8)
        return f"{share:,.0f} so'm"

    def platform_share_som(self, obj):
        if not obj.amount:
            return "-"
        platform = int(obj.amount * 0.2)
        return f"{platform:,.0f} so'm"

    def created_at_display(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S") if obj.created_at else "-"
    created_at_display.short_description = "Created At"




# ---------------- MentorBalanceAdmin ----------------
@admin.register(MentorBalance)
class MentorBalanceAdmin(admin.ModelAdmin):
    list_display = ("mentor", "formatted_balance", "updated_at", "id")
    search_fields = ("mentor__username", "mentor__email")

    def formatted_balance(self, obj):
        return f"{obj.balance:,} so'm"
    formatted_balance.short_description = "Balance"





# ---------------- MentorBalanceHistoryAdmin ----------------
@admin.register(MentorBalanceHistory)
class MentorBalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ("mentor", "formatted_amount", "description", "created_at", "id")
    search_fields = ("mentor__username",)

    def formatted_amount(self, obj):
        return f"{obj.amount:,} so'm"
    formatted_amount.short_description = "Amount"




# ---------------- WithdrawRequestAdmin ----------------
@admin.register(WithdrawRequest)
class WithdrawRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "mentor", "amount", "status", "created_at")
    readonly_fields = ("multicard_transaction_id", "multicard_uuid")
    actions = ["approve_withdraw_requests"]

    def approve_withdraw_requests(self, request, queryset):
        for withdraw in queryset.filter(status="PENDING"):
            try:
                mentor_profile = withdraw.mentor.mentor_profile
            except MentorProfile.DoesNotExist:
                self.message_user(request, f"{withdraw.mentor.get_full_name()} uchun mentor profile topilmadi", level=messages.ERROR)
                continue

            try:
                res = mentor_create_payout(mentor_profile, withdraw.amount, withdraw.id)
                if not res.get("success"):
                    error_msg = res.get("error", {}).get("details", "Unknown error")
                    self.message_user(request, f"{withdraw.mentor.get_full_name()} to‘lov muvaffaqiyatsiz: {error_msg}", level=messages.ERROR)
                    continue

                data = res.get("data", res.get("confirmed", {}).get("data", {}))

                withdraw.status = "APPROVED"
                withdraw.multicard_transaction_id = data.get("id")
                withdraw.multicard_uuid = data.get("uuid")
                withdraw.save()

                self.message_user(request, f"{withdraw.mentor.get_full_name()} yechib olish muvaffaqiyatli", level=messages.SUCCESS)

            except Exception as e:
                self.message_user(request, f"{withdraw.mentor.get_full_name()} to‘lov xato: {str(e)}", level=messages.ERROR)

    approve_withdraw_requests.short_description = "Approve selected Withdraw Requests"









# ---------------- Platform Balance ----------------
@admin.register(PlatformBalance)
class PlatformBalanceAdmin(admin.ModelAdmin):
    list_display = ("balance_display", "updated_at", "id")
    readonly_fields = ("balance_display", "updated_at")
    search_fields = ()

    def balance_display(self, obj):
        return f"{obj.balance:,} so'm"
    balance_display.short_description = "Balance"





# ---------------- Platform Balance History ----------------
@admin.register(PlatformBalanceHistory)
class PlatformBalanceHistoryAdmin(admin.ModelAdmin):
    list_display = ("amount_display", "description", "created_at", "id")
    readonly_fields = ("amount_display", "description", "created_at")
    search_fields = ("description",)
    list_filter = ("created_at",)

    def amount_display(self, obj):
        return f"{obj.amount:,} so'm"
    amount_display.short_description = "Amount"