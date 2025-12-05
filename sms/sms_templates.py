from django.template.loader import render_to_string

def render_sms_template(template_name: str, context: dict):
    return render_to_string(template_name, context).strip()
