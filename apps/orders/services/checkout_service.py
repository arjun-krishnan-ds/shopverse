# apps/orders/services/checkout_service.py
"""
CheckoutService — Production-safe order creation.

Key design decisions:
- Stock is validated here but NOT deducted.
- Deduction happens inside the Stripe webhook after payment confirmation.
- Cart is NOT cleared here; it is cleared inside the webhook after payment.
- For COD orders, stock IS deducted and cart IS cleared here because
  there is no async payment confirmation step.
"""

from decimal import Decimal

from django.db import transaction

from apps.orders.models import Order, OrderItem
from apps.products.models import ProductVariant
from apps.orders.exceptions import InsufficientStock
from apps.delivery.services.delivery_service import DeliveryService
from apps.orders.exceptions import InsufficientStock
from apps.cart.utils import get_or_create_cart
class CheckoutService:

    @staticmethod
    def create_order_from_cart(
        user,
        address,
        request=None,
    ):
        """
        Create an order from the user's active cart.

        Behaviour by payment method:
        - stripe : validate stock only → order PENDING → Stripe handles the rest
        - cod    : validate + deduct stock + clear cart immediately
        """



        # ─────────────────────────────────────────────────────
        # GUARD: request required to locate the correct cart
        # ─────────────────────────────────────────────────────
        if not request:
            raise ValueError(
                "Request object is required for checkout."
            )

        cart = get_or_create_cart(request, user)

        if not cart or not cart.items.exists():
            raise Exception("Cart is empty.")

        # ─────────────────────────────────────────────────────
        # RESOLVE PAYMENT METHOD
        # Peek at the POST data so we know whether to deduct
        # stock immediately (COD) or defer (Stripe).
        # ─────────────────────────────────────────────────────
        payment_method = "cod"
        if request and hasattr(request, "POST"):
            payment_method = request.POST.get(
                "payment_method", "cod"
            )

        cart_items = cart.items.select_related(
            "variant",
            "variant__product",
        )

        with transaction.atomic():

            # ─────────────────────────────────────────────────
            # TOTALS
            # ─────────────────────────────────────────────────
            subtotal = cart.subtotal or Decimal("0.00")

            shipping_cost = DeliveryService.calculate_delivery(subtotal)

            final_total = subtotal + shipping_cost

            # ─────────────────────────────────────────────────
            # CREATE ORDER (status = PENDING always)
            # ─────────────────────────────────────────────────
            order = Order.objects.create(
                user=user,
                address=address,
                shipping_cost=shipping_cost,
                total_amount=final_total,
                status=Order.Status.PENDING,
            )

            # ─────────────────────────────────────────────────
            # VALIDATE STOCK + CREATE ORDER ITEMS
            # We lock each variant row to prevent race conditions
            # on concurrent checkouts for the same product.
            # ─────────────────────────────────────────────────
            for cart_item in cart_items:

                variant = (
                    ProductVariant.objects
                    .select_for_update()
                    .select_related("product")
                    .get(id=cart_item.variant.id)
                )

                # Stock validation — always performed regardless of payment method
                if variant.stock < cart_item.quantity:
                    raise InsufficientStock(
                        f"Insufficient stock for "
                        f"'{variant.product.name}'. "
                        f"Available: {variant.stock}, "
                        f"Requested: {cart_item.quantity}."
                    )

                # ─────────────────────────────────────────────
                # COD: deduct stock immediately because there
                # is no asynchronous payment confirmation.
                # Stripe: defer — deduction happens in webhook.
                # ─────────────────────────────────────────────
                if payment_method == "cod":
                    ProductVariant.objects.filter(
                        id=variant.id
                    ).update(
                        stock=variant.stock - cart_item.quantity
                    )

                OrderItem.objects.create(
                    order=order,
                    product_variant=variant,
                    product_name=variant.product.name,
                    sku=variant.sku,
                    price=variant.price,
                    quantity=cart_item.quantity,
                    total_price=variant.price * cart_item.quantity,
                )

            # ─────────────────────────────────────────────────
            # RECALCULATE TOTAL (picks up item-level prices)
            # ─────────────────────────────────────────────────
            order.update_total()

            # ─────────────────────────────────────────────────
            # COD: clear cart immediately.
            # Stripe: cart cleared inside webhook after payment.
            # ─────────────────────────────────────────────────
            if payment_method == "cod":
                cart.items.all().delete()

            return order