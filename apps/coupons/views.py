from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.cart.utils import get_or_create_cart
from .services.coupon_service import CouponService


# =========================================================
# APPLY COUPON
# =========================================================

@require_POST
def apply_coupon(request):

    code = None

    # Support both JSON and form requests
    if request.content_type == "application/json":
        import json
        data = json.loads(request.body)
        code = data.get("coupon_code")
    else:
        code = request.POST.get("coupon")

    if not code:
        return JsonResponse({
            "success": False,
            "message": "Coupon code required"
        })

    cart = get_or_create_cart(request)
    cart_total = cart.subtotal

    try:

        coupon = CouponService.validate_coupon(
            code,
            cart_total
        )

        discount = CouponService.calculate_discount(
            coupon,
            cart_total
        )

        request.session["coupon_code"] = coupon.code
        request.session["discount"] = float(discount)

        new_total = float(cart_total) - float(discount)

        return JsonResponse({
            "success": True,
            "coupon": coupon.code,
            "discount": float(discount),
            "cart_total": float(new_total),
            "cart_discount": float(discount),
            "message": "Coupon applied successfully"
        })

    except Exception as e:

        return JsonResponse({
            "success": False,
            "message": str(e)
        })


# =========================================================
# REMOVE COUPON
# =========================================================

@require_POST
def remove_coupon(request):

    cart = get_or_create_cart(request)
    cart_total = cart.subtotal

    request.session.pop("coupon_code", None)
    request.session.pop("discount", None)

    return JsonResponse({
        "success": True,
        "cart_total": float(cart_total),
        "cart_discount": 0,
        "message": "Coupon removed"
    })