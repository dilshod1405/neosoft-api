import re
from django.core.exceptions import ValidationError


def validate_uzb_card_number(card_number: str):
    number = card_number.replace(" ", "").replace("-", "")

    if not number.isdigit():
        raise ValidationError("Karta raqami faqat raqamlardan iborat bo‘lishi kerak.")

    if len(number) != 16:
        raise ValidationError("Karta raqami 16 xonadan iborat bo‘lishi kerak.")

    # Uzcard
    if number.startswith("8600"):
        return "uzcard"

    # Humo
    if number.startswith("9860"):
        return "humo"

    # Visa
    if number.startswith("4"):
        return "visa"

    # MasterCard (51-55)
    if 51 <= int(number[:2]) <= 55:
        return "mastercard"

    # MasterCard (2221-2720)
    if 2221 <= int(number[:4]) <= 2720:
        return "mastercard"

    raise ValidationError("Noto‘g‘ri yoki qo‘llab-quvvatlanmaydigan karta raqami.")
