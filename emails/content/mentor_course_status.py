from celery import shared_task
from emails.send_custom_email import send_custom_email


# ===============================================================================
#         SENDS AN EMAIL TO THE CONSTRUCTOR BASED ON THE COURSE STATUS
# ===============================================================================

@shared_task
def send_course_status_email(instance, language='uz'):
    """
    Sends an email to the instructor based on the course status and language.
    """
    subject_map = {
        'approved': {
            'uz': 'Kursingiz faollashtirildi',
            'ru': 'Ваш курс активирован',
        },
        'rejected': {
            'uz': 'Kursingiz rad etildi',
            'ru': 'Ваш курс отклонен',
        }
    }

    if instance.status == 'approved':
        context = {
            'full_name': instance.course.instructor.user.full_name,
            'course': instance.course.title_uz,
        }
        send_custom_email(
            subject=subject_map['approved'].get(language, 'Kursingiz faollashtirildi !'),
            template_name='courses/email/course_approved.html',
            context=context,
            to_email=instance.course.instructor.user.email,
        )
    elif instance.status == 'rejected' and instance.rejection_reason:
        context = {
            'full_name': instance.course.instructor.user.full_name,
            'course': instance.course.title_uz,
            'reason': instance.rejection_reason
        }
        send_custom_email(
            subject=subject_map['rejected'].get(language, 'Kursingiz rad etildi !'),
            template_name='courses/email/course_rejected.html',
            context=context,
            to_email=instance.course.instructor.user.email,
        )