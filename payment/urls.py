from django.urls import path
from payment.payme.payme_callback_webhook import PaymeCallBackAPIView
from payment.payme.create_order_transaction import CreateOrderTransactionAPIView
from payment.mentors.views import MentorBalanceDetailAPIView
from .views import PlatformBalanceDetailAPIView
from payment.click.create_order_transaction import CreateClickOrderTransactionView
from payment.click.click_callback_webhook import ClickCallBackAPIView
from payment.uzum.check_transaction_webhook import UzumCheckView
from payment.uzum.create_transaction_webhook import UzumCreateView
from payment.uzum.confirm_transaction_webhook import UzumConfirmView
from payment.uzum.reverse_transaction_webhook import UzumReverseView
from payment.uzum.status_transaction_webhook import UzumStatusView
from payment.uzum.create_order_transaction import CreateOrderTransactionUzumAPIView

urlpatterns = [

    #------------------- Platform API ---------------------#
    path("platform/balance/", PlatformBalanceDetailAPIView.as_view(), name="platform-balance-transactions"),
    


    #------------------- Student API ----------------------#
    path("payme/callback/", PaymeCallBackAPIView.as_view(), name="payme-callback"),
    path("click/callback/", ClickCallBackAPIView.as_view()),
    
    path("payme/create-order/", CreateOrderTransactionAPIView.as_view(), name="payme-create-order"),
    path("click/create-order/", CreateClickOrderTransactionView.as_view(), name='click-create-order'),

    path("uzum/check/", UzumCheckView.as_view(), name="uzum-check-transaction"),
    path("uzum/create/", UzumCreateView.as_view(), name="uzum-create-transaction"),
    path("uzum/confirm/", UzumConfirmView.as_view(), name="uzum-confirm-transaction"),
    path("uzum/reverse/", UzumReverseView.as_view(), name="uzum-reverse-transaction"),
    path("uzum/status/", UzumStatusView.as_view(), name="uzum-status-transaction"),
    path("uzum/create-order/", CreateOrderTransactionUzumAPIView.as_view(), name="uzum-create-order"),



    #------------------- Mentor API -----------------------#
    path("mentor/balance/", MentorBalanceDetailAPIView.as_view(), name="mentor-balance-transactions"),

]
