from django.db import transaction
from django.db.models import F

from apps.products.models import ProductVariant


class OrderService:

    @staticmethod
    def cancel_order(order):
        """
        Cancel an order and restore product stock.
        """

        if order.status not in ["pending", "paid", "processing"]:
            raise Exception("Order cannot be cancelled")

        with transaction.atomic():

            # Restore stock for each order item
            for item in order.items.select_related("product_variant"):

                if item.product_variant:

                    ProductVariant.objects.filter(
                        id=item.product_variant.id
                    ).update(
                        stock=F("stock") + item.quantity
                    )

            order.status = "cancelled"
            order.save(update_fields=["status"])