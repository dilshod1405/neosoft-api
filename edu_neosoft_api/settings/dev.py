from .base import *
from decouple import config

DEBUG = True
ALLOWED_HOSTS = ["*"]


RESEND_API_KEY = config('RESEND_API_KEY')

VDOCIPHER_API_BASE = config('VDOCIPHER_API_BASE')
VDOCIPHER_API_KEY = config('VDOCIPHER_API_KEY')
VDOCIPHER_WEBHOOK_SECRET = config('VDOCIPHER_WEBHOOK_SECRET')



EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.resend.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "resend"
EMAIL_HOST_PASSWORD = "re_Let9mbkE_KwPPRZEeZ9Pga7iFW9zh8qkc"
DEFAULT_FROM_EMAIL = "info@neosoft.uz"