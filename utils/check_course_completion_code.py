from content.students.models import CompletionPromoCode


def check_completion_promo(course, code):
    promo = CompletionPromoCode.objects.filter(code=code, is_used=False).first()
    if promo and promo.is_valid:
        price_after_discount = promo.discount.calculate_discounted_price(course.price)
        promo.mark_used()
        return price_after_discount
    return course.price
