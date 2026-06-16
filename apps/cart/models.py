from django.conf import settings
from django.db import models

from apps.core.models import BaseModel
from apps.products.models import ProductVariant


User = settings.AUTH_USER_MODEL


class Cart(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="carts",
        db_index=True
    )

    session_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True
    )

    # Coupon support (safe addition)
    coupon = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="carts"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        if self.user:
            return f"Cart ({self.user})"
        return f"Cart ({self.session_id})"

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def discount_amount(self):

        if not self.coupon:
            return 0

        if self.coupon.discount_type == "percentage":
            discount = (self.subtotal * self.coupon.discount_value) / 100

            if self.coupon.max_discount:
                discount = min(discount, self.coupon.max_discount)

            return discount

        if self.coupon.discount_type == "fixed":
            return self.coupon.discount_value

        return 0

    @property
    def total(self):
        return max(self.subtotal - self.discount_amount, 0)


class CartItem(BaseModel):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        db_index=True
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "variant")

    def __str__(self):
        return f"{self.variant.sku} x {self.quantity}"

    @property
    def total_price(self):
        return self.variant.price * self.quantity