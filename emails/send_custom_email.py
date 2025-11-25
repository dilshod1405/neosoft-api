from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

# ===================================================================================
# Send Email Template
# ===================================================================================
def send_custom_email(subject, template_name, context, to_email, from_email=None, cc=None, bcc=None):
    """
    Generalized function to send HTML emails with plain-text fallback.
    """
    if from_email is None:
        from_email = settings.DEFAULT_FROM_EMAIL

    # Render HTML content
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)

    # Initialize email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email],
        cc=cc or [],
        bcc=bcc or [],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

EMAIL_CONFIG = {
    'default_from': settings.DEFAULT_FROM_EMAIL,
    # 'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@edvent.uz'),
    # 'marketing_email': getattr(settings, 'MARKETING_EMAIL', 'marketing@edvent.uz'),
}