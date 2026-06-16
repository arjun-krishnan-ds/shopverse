from .stripe_gateway import StripeGateway


class PaymentService:
    """
    Central payment handler.

    Responsible for delegating payment creation
    to the correct payment gateway.

    Example flow:

    CheckoutService
        ↓
    PaymentService
        ↓
    StripeGateway / RazorpayGateway / etc
    """

    gateways = {
        "stripe": StripeGateway,
    }

    @classmethod
    def create_payment(cls, order, gateway="stripe"):
        """
        Create a payment session for an order.

        Returns:
            payment_url (str)
        """

        if not order:
            raise ValueError("Order is required")

        if order.total_amount <= 0:
            raise ValueError("Invalid order amount")

        gateway_class = cls.gateways.get(gateway)

        if not gateway_class:
            raise ValueError(f"Unsupported payment gateway: {gateway}")

        gateway_instance = gateway_class()

        return gateway_instance.create_payment(order)