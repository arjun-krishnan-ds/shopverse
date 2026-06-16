from django.db import models
from apps.core.models import BaseModel
from apps.orders.models import Order


class Payment(BaseModel):

    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    PAYMENT_GATEWAYS = [
        ("stripe", "Stripe"),
        ("razorpay", "Razorpay"),
        ("paypal", "PayPal"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    gateway = models.CharField(
        max_length=20,
        choices=PAYMENT_GATEWAYS
    )

    payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default="pending"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    currency = models.CharField(
        max_length=10,
        default="usd"
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.gateway}"
    
class Refund(BaseModel):

    STATUS = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("processed", "Processed"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="refunds"
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default="pending"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund #{self.id} - {self.order.id}"