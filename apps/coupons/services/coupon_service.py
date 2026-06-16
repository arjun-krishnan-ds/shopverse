from decimal import Decimal
from apps.coupons.models import Coupon


class CouponService:

    @staticmethod
    def validate_coupon(code, cart_total):
        coupon = Coupon.objects.filter(code__iexact=code).first()
        if not coupon:
            raise Exception("Invalid coupon code")
        if not coupon.is_valid(cart_total):
            raise Exception("Coupon is not valid or has expired")
        return coupon

    @staticmethod
    def calculate_discount(coupon, cart_total):
        if coupon.discount_type == "percentage":
            discount = cart_total * (coupon.discount_value / Decimal(100))
            if coupon.max_discount:
                discount = min(discount, coupon.max_discount)
        else:
            discount = coupon.discount_value
        return discount

    @staticmethod
    def apply_coupon(cart_total, code):
        coupon = CouponService.validate_coupon(code, cart_total)
        discount = CouponService.calculate_discount(coupon, cart_total)
        return discount, coupon