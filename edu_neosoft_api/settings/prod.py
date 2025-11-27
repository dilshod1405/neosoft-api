from ..base import *
from celery.schedules import crontab

DEBUG = True
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


REDIS_HOST = config("REDIS_HOST", default="localhost")
REDIS_PORT = config("REDIS_PORT", default="6379")
REDIS_DB = config("REDIS_DB", default="0")
REDIS_PASSWORD = config("REDIS_PASSWORD", default=None)
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"


CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60


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


