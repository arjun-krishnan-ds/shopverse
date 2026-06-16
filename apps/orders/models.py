from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.core.models import BaseModel
from apps.products.models import ProductVariant
from apps.accounts.models import Address
from django.db import transaction

# =========================================================
# ORDER
# =========================================================


class Order(BaseModel):

    order_number = models.CharField(
        max_length=20, unique=True, editable=False, db_index=True
    )

    # =====================================================
    # STATUS
    # =====================================================

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True
    )

    # =====================================================
    # PAYMENT
    # =====================================================

    PAYMENT_METHODS = [
        ("cod", "Cash on Delivery"),
        ("razorpay", "Razorpay"),
        ("stripe", "Stripe"),
    ]

    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default="cod"
    )

    is_paid = models.BooleanField(default=False)

    payment_reference = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )

    stripe_session_id = models.CharField(
        max_length=255, blank=True, null=True, db_index=True
    )

    # =====================================================
    # USER / ADDRESS
    # =====================================================

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name="orders"
    )

    # =====================================================
    # TOTALS
    # =====================================================

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    coupon_code = models.CharField(max_length=50, null=True, blank=True)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # =====================================================
    # DELIVERY / TRACKING
    # =====================================================

    courier_name = models.CharField(max_length=100, blank=True, null=True)

    tracking_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)

    estimated_delivery = models.DateField(null=True, blank=True)

    shipped_at = models.DateTimeField(null=True, blank=True)

    delivered_at = models.DateTimeField(null=True, blank=True)

    # =====================================================
    # META
    # =====================================================

    class Meta:
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["tracking_id"]),
        ]
        ordering = ["-created_at"]

    # =====================================================
    # SAVE (ORDER NUMBER GENERATION)
    # FIX C1: The atomic block now wraps super().save() so the
    # select_for_update lock is held until the row is actually
    # written. Previously the lock was released before save(),
    # creating a race window where two concurrent checkouts could
    # generate the same order_number and one would crash.
    # Sort by -id (integer) not -order_number (string) to ensure
    # correct ordering regardless of zero-padding.
    # =====================================================

    def save(self, *args, **kwargs):
        if not self.order_number:
            with transaction.atomic():
                last = (
                    Order.objects.select_for_update()
                    .filter(order_number__startswith=f"ORD-{timezone.now().year}")
                    .order_by("-id")   # integer sort — always correct
                    .first()
                )
                new_number = (
                    int(last.order_number.split("-")[-1]) + 1
                ) if last else 1
                self.order_number = (
                    f"ORD-{timezone.now().year}-{new_number:06d}"
                )
                super().save(*args, **kwargs)
            return
        super().save(*args, **kwargs)

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def subtotal(self):
        """Sum of all order items."""
        return sum(item.total_price for item in self.items.all())

    @property
    def total(self):
        """Consistent frontend accessor."""
        return self.total_amount

    @property
    def discount(self):
        return self.discount_amount

    @property
    def delivery_fee(self):
        return self.shipping_cost

    @property
    def shipping_address(self):
        return str(self.address) if self.address else ""

    @property
    def is_delivered(self):
        return self.status == self.Status.DELIVERED

    @property
    def is_cancelled(self):
        return self.status == self.Status.CANCELLED

    @property
    def can_be_cancelled(self):
        return self.status in [
            self.Status.PENDING,
            self.Status.PAID,
            self.Status.PROCESSING,
        ]

    @property
    def is_shipped(self):
        return self.status in [
            self.Status.SHIPPED,
            self.Status.OUT_FOR_DELIVERY,
            self.Status.DELIVERED,
        ]

    @property
    def status_index(self):
        """Used for frontend progress tracker."""
        mapping = {
            "pending": 0,
            "paid": 1,
            "processing": 1,
            "shipped": 2,
            "out_for_delivery": 3,
            "delivered": 4,
        }
        return mapping.get(self.status, 0)

    # =====================================================
    # TOTAL CALCULATION
    # =====================================================

    def update_total(self):
        subtotal = sum(item.total_price for item in self.items.all())
        final_total = subtotal - self.discount_amount + self.shipping_cost
        self.total_amount = max(final_total, 0)
        self.save(update_fields=["total_amount"])

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):
        return f"{self.order_number} - {self.user}"


# =========================================================
# ORDER ITEM
# =========================================================


class OrderItem(BaseModel):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.SET_NULL, null=True
    )

    product_name = models.CharField(max_length=255)

    sku = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.PositiveIntegerField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    # =====================================================
    # SAVE
    # =====================================================

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)

    # =====================================================
    # STRING
    # =====================================================

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"