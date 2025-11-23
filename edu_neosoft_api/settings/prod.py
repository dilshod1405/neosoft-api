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
PAYME_ID = "68f4956288f28864c0662548"
PAYME_KEY = "nio94C82N8fkO4EsvHc9r7?DnI4QD7irGR??"
PAYME_ACCOUNT_MODEL = "payment.models.Transaction"
PAYME_ACCOUNT_FIELD = "id"
PAYME_AMOUNT_FIELD = "amount"
PAYME_ONE_TIME_PAYMENT = True