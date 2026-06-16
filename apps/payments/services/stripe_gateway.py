# apps/payments/stripe_gateway.py

import stripe

from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeGateway:

    def create_payment(self, order) -> str:
        """
        Create Stripe Checkout Session.

        Charges the FINAL order amount:
            subtotal
            - discount
            + shipping

        Uses INR (paise) when STRIPE_CURRENCY="inr".

        Returns:
            Stripe hosted checkout URL.
        """

        amount_in_smallest_unit = int(
            order.total_amount * 100
        )

        customer_email = None

        if (
            order.user
            and order.user.email
        ):
            customer_email = order.user.email

        session = stripe.checkout.Session.create(

            payment_method_types=["card"],

            mode="payment",

            customer_email=customer_email,

            customer_creation="always",

            line_items=[
                {
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY.lower(),

                        "product_data": {
                            "name": (
                                f"Order "
                                f"{order.order_number}"
                            ),

                            "description": (
                                f"{order.items.count()} item(s)"
                            ),
                        },

                        "unit_amount": (
                            amount_in_smallest_unit
                        ),
                    },

                    "quantity": 1,
                }
            ],

            success_url=(
                f"{settings.FRONTEND_URL}"
                f"/orders/success/"
                f"?order_id={order.id}"
            ),

            cancel_url=(
                f"{settings.FRONTEND_URL}"
                f"/orders/payment-cancelled/"
                f"?order_id={order.id}"
            ),

            metadata={
                "order_id": str(order.id),
                "order_number": order.order_number,
                "user_id": str(order.user_id),
            },

            billing_address_collection="required",

            allow_promotion_codes=False,
        )

        order.stripe_session_id = session.id

        order.save(
            update_fields=[
                "stripe_session_id",
            ]
        )

        return session.url