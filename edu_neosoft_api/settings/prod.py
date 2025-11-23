from .base import *
from celery.schedules import crontab

DEBUG = False
ALLOWED_HOSTS = ["edu.neosoft.uz", "mentor.neosoft.uz", "54.app.ioedge.host"]

CSRF_TRUSTED_ORIGINS = [
    "https://edu.neosoft.uz",
    "https://mentor.neosoft.uz",
    "https://54.app.ioedge.host"
]


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://edu.neosoft.uz",
    "https://mentor.neosoft.uz",
    "https://54.app.ioedge.host"
]

CORS_ALLOW_CREDENTIALS = True




CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'


CELERY_BEAT_SCHEDULE = {
    'update-bestseller-status-every-2-days': {
        'task': 'content.tasks.update_bestseller_status',
        'schedule': crontab(minute=0, hour=0, day_of_week='*', day_of_month='*/2'),  # Every 2 days at midnight
    },
}


# Run this command for schedule tasks: celery -A edu_neosoft_api beat --loglevel=info
# Run this command for worker: celery -A edu_neosoft_api worker --loglevel=info





PAYME_USE_CUSTOM_CALLBACK = True
PAYME_ID = config('PAYME_ID')
PAYME_KEY = config('PAYME_KEY')
PAYME_ACCOUNT_MODEL = "payment.models.Transaction"
PAYME_ACCOUNT_FIELD = "id"
PAYME_AMOUNT_FIELD = "amount"
PAYME_ONE_TIME_PAYMENT = True


RESEND_API_KEY = config('RESEND_API_KEY')

VDOCIPHER_API_BASE = config('VDOCIPHER_API_BASE')
VDOCIPHER_API_KEY = config('VDOCIPHER_API_KEY')
VDOCIPHER_WEBHOOK_SECRET = config('VDOCIPHER_WEBHOOK_SECRET')



EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.resend.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "resend"
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')