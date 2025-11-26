from django.conf import settings
from django.template.loader import render_to_string
from weasyprint import HTML
import os
import uuid

def generate_contract_pdf(context):
    html = render_to_string("contracts/contract.html", context)

    filename = f"contract_{uuid.uuid4()}.pdf"
    filepath = os.path.join(settings.MEDIA_ROOT, "contracts", filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    HTML(string=html).write_pdf(filepath)

    return filepath
