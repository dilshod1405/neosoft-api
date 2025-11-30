from celery import shared_task
from utils.sender_notification import remove_expired_notifications

@shared_task
def clean_expired_notifications():
    remove_expired_notifications()
