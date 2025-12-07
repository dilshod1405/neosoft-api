from django.urls import path
from payment.payme.payme_callback_webhook import PaymeCallBackAPIView
from payment.payme.create_order_transaction import CreateOrderTransactionAPIView
from payment.mentors.views import MentorBalanceDetailAPIView
from .views import PlatformBalanceDetailAPIView, CreateUniversalPaymentAPIView
from payment.click.create_order_transaction import CreateClickOrderTransactionView
from payment.click.click_callback_webhook import ClickCallBackAPIView
from payment.uzum.check_transaction_webhook import UzumCheckView
from payment.uzum.create_transaction_webhook import UzumCreateView
from payment.uzum.confirm_transaction_webhook import UzumConfirmView
from payment.uzum.reverse_transaction_webhook import UzumReverseView
from payment.uzum.status_transaction_webhook import UzumStatusView
from payment.manager.views import WithdrawRequestListView, ApproveWithdrawRequestView
from payment.mentors.views import MentorWithdrawRequestCreateView, MentorWithdrawHistoryView
from payment.students.views import StudentTransactionHistoryView

urlpatterns = [

    #------------------- Platform API ---------------------#
    path("platform/balance/", PlatformBalanceDetailAPIView.as_view(), name="platform-balance-transactions"),
    


    #------------------- Student API ----------------------#
    path("payme/callback/", PaymeCallBackAPIView.as_view(), name="payme-callback"),
    path("click/callback/", ClickCallBackAPIView.as_view()),

    path("uzum/check/", UzumCheckView.as_view(), name="uzum-check-transaction"),
    path("uzum/create/", UzumCreateView.as_view(), name="uzum-create-transaction"),
    path("uzum/confirm/", UzumConfirmView.as_view(), name="uzum-confirm-transaction"),
    path("uzum/reverse/", UzumReverseView.as_view(), name="uzum-reverse-transaction"),
    path("uzum/status/", UzumStatusView.as_view(), name="uzum-status-transaction"),

    path("create-order-transaction/", CreateUniversalPaymentAPIView.as_view(), name="payment-create"),

    path("student/transactions/", StudentTransactionHistoryView.as_view(), name="student-transaction-history"),


    #------------------- Mentor API -----------------------#
    path("mentor/balance/", MentorBalanceDetailAPIView.as_view(), name="mentor-balance-transactions"),
    path("mentor/withdraw/", MentorWithdrawRequestCreateView.as_view(), name="mentor-withdraw-request"),
    path("mentor/withdraw/history/", MentorWithdrawHistoryView.as_view(), name="mentor-withdraw-history"),



    #------------------- MANAGER API -----------------------#
    path("admin/list-withdraw-requests/", WithdrawRequestListView.as_view(), name="withdraw-request-list"),
    path("admin/withdraw-requests/<int:pk>/approve/", ApproveWithdrawRequestView.as_view(), name="withdraw-request-approve"),

]
