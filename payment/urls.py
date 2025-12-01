from django.urls import path
from payment.payme.payme_callback_webhook import PaymeCallBackAPIView
from payment.payme.create_order_transaction import CreateOrderTransactionAPIView
from payment.mentors.views import MentorTransactionsAPIView
from .views import PlatformBalanceAPIView

urlpatterns = [

    path("platform/balance/", PlatformBalanceAPIView.as_view(), name="platform-balance"),
    

    path("payme/callback/", PaymeCallBackAPIView.as_view(), name="payme-callback"),

    path("payme/create-order/", CreateOrderTransactionAPIView.as_view(), name="create-order"),


    path("mentor/transactions/", MentorTransactionsAPIView.as_view(), name="mentor-transactions"),

]
