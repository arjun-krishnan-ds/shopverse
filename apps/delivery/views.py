# apps/delivery/views.py

from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from apps.delivery.services.delivery_service import DeliveryService


@require_GET
def delivery_fee(request):

    cart_total = request.GET.get("cart_total", "0")
    pincode = request.GET.get("pincode", "")

    try:
        cart_total = Decimal(cart_total)
    except (InvalidOperation, TypeError):
        cart_total = Decimal("0.00")

    delivery_fee = DeliveryService.calculate_delivery(cart_total)

    return JsonResponse({
        "success": True,
        "delivery_fee": str(delivery_fee),
        "pincode": pincode,
        "cod_available": True,
        "estimated_days": 3,
    })