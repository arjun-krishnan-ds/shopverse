from django.db import models
from apps.core.models import BaseModel


class DeliveryRule(BaseModel):

    name = models.CharField(max_length=100)

    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    is_active = models.BooleanField(default=True)

    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority rules are applied first"
    )

    class Meta:
        ordering = ["-priority", "-min_order_value"]

    def __str__(self):
        return f"{self.name} (Min: {self.min_order_value})"