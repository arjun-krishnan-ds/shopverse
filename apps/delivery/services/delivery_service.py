# apps/delivery/services/delivery_service.py

from decimal import Decimal

from apps.delivery.models import DeliveryRule


class DeliveryService:

    @staticmethod
    def calculate_delivery(cart_total):

        rule = (
            DeliveryRule.objects
            .filter(
                is_active=True,
                min_order_value__lte=cart_total
            )
            .order_by("-min_order_value")
            .first()
        )

        if rule:
            return rule.delivery_fee

        return Decimal("0.00")