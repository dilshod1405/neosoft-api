def mask_card_number(card_number: str):
    """
    8600123456789999 -> 8600 **** **** 9999
    """
    if not card_number or len(card_number) < 8:
        return card_number

    first4 = card_number[:4]
    last4 = card_number[-4:]
    return f"{first4} **** **** {last4}"
