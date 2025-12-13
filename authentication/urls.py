from django.urls import path, include
from .views import (
    RegisterView, 
    LoginView,
    RefreshView,
    ActivationView,
    ResendCodeView,
    LogoutView
)
from authentication.google.login import GoogleLoginView



urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),

    path('activate/', ActivationView.as_view(), name='activate'),

    path('resendcode/', ResendCodeView.as_view(), name='resend_code'),

    path('login/', LoginView.as_view(), name='login'),

    path('token/refresh/', RefreshView.as_view(), name='token_refresh'),

    path('logout/', LogoutView.as_view(), name='logout'),

    path("google/login/", GoogleLoginView.as_view(), name='google-login'),

    path("student/", include('authentication.students.urls'))
]
