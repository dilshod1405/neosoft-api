from django.db import models
from django.utils import timezone
import string, random

def generate_promo_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

