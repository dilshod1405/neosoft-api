from django.urls import path
from payment.payme.payme_callback_webhook import PaymeCallBackAPIView
from payment.payme.create_order_transaction import CreateOrderTransactionAPIView
from payment.mentors.views import MentorBalanceDetailAPIView
from .views import PlatformBalanceDetailAPIView
from payment.click.create_order_transaction import CreateClickOrderTransactionView
from payment.click.click_callback_webhook import ClickCallBackAPIView

urlpatterns = [

    #------------------- Platform API ---------------------#
    path("platform/balance/", PlatformBalanceDetailAPIView.as_view(), name="platform-balance"),
    


    #------------------- Student API ----------------------#
    path("payme/callback/", PaymeCallBackAPIView.as_view(), name="payme-callback"),
    path("click/callback/", ClickCallBackAPIView.as_view()),
    
    path("payme/create-order/", CreateOrderTransactionAPIView.as_view(), name="create-order"),
    path("click/create-order/", CreateClickOrderTransactionView.as_view()),



    #------------------- Mentor API -----------------------#
    path("mentor/balance/", MentorBalanceDetailAPIView.as_view(), name="mentor-transactions"),

]
