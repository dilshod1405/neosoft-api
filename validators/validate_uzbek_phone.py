import re
from django.core.exceptions import ValidationError

def validate_uzbek_phone(value):
    pattern = r'^\+998\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError("Telefon raqam '+9989012345678' formatida bo‘lishi kerak.")