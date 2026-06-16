from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel


class Coupon(BaseModel):

    DISCOUNT_TYPE = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_cart_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    used_count = models.PositiveIntegerField(
        default=0
    )

    valid_from = models.DateTimeField()

    valid_to = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    def is_valid(self, cart_total):

        now = timezone.now()

        if not self.is_active:
            return False

        if now < self.valid_from or now > self.valid_to:
            return False

        if cart_total < self.min_cart_value:
            return False

        if self.usage_limit and self.used_count >= self.usage_limit:
            return False

        return True

    def __str__(self):
        return self.code