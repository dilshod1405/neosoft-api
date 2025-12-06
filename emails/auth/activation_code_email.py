from celery import shared_task
from emails.send_custom_email import send_custom_email
from random import randint
import logging
from authentication.models import CustomUser
from utils.get_redis import get_redis

logger = logging.getLogger(__name__)

def generate_code():
    return randint(100000, 999999)

@shared_task(bind=True, max_retries=0)
def activation_code_email(self, user_id, language='uz'):
    try:
        user = CustomUser.objects.get(id=user_id)
        code = generate_code()

        if language not in ['uz', 'ru']:
            language = 'uz'

        subject_map = {
            'uz': 'Aktivlashtirish kodi',
            'ru': 'Код активации',
        }

        subject = subject_map.get(language, 'Registration Code')
        template_name = f'authentication/activation_code_{language}.html'

        context = {
            'first_name': user.first_name,
            'code': code,
        }

        redis_client = get_redis()
        redis_client.setex(f"activation_code:{user_id}", 120, str(code))

        send_custom_email(
            subject=subject,
            template_name=template_name,
            context=context,
            to_email=user.email,
        )

        return code

    except CustomUser.DoesNotExist:
        raise self.retry(countdown=60)
    except Exception as e:
        raise self.retry(countdown=60, exc=e)
