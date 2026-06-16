from django.db import models
import uuid

from django.conf import settings
from django.db.models import Min, Q

from apps.core.models import BaseModel
from apps.core.utils import generate_unique_slug


class Category(BaseModel):

    name = models.CharField(max_length=255, unique=True)

    slug = models.SlugField(unique=True)

    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )

    class Meta:
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["parent"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(BaseModel):

    name = models.CharField(max_length=255, unique=True)

    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)

    logo = models.ImageField(upload_to="brands/", blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(Brand, self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(BaseModel):

    name = models.CharField(max_length=255, db_index=True)

    slug = models.SlugField(unique=True, db_index=True)

    brand = models.ForeignKey(
        Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    description = models.TextField()

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name"]),
        ]

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = generate_unique_slug(Product, self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # -----------------------------
    # IMAGE HELPERS
    # -----------------------------

    @property
    def primary_image(self):

        image = self.images.filter(is_primary=True).first()

        if image:
            return image

        return self.images.first()

    # -----------------------------
    # REVIEW HELPERS
    # -----------------------------

    @property
    def average_rating(self):

        reviews = self.reviews.filter(is_approved=True)

        if not reviews.exists():
            return 0

        total = sum(review.rating for review in reviews)

        return round(total / reviews.count(), 2)

    @property
    def review_count(self):

        return self.reviews.filter(is_approved=True).count()

    # -----------------------------
    # PRICE HELPER
    # -----------------------------

    @property
    def lowest_price(self):

        result = self.variants.filter(is_active=True).aggregate(Min("price"))

        return result["price__min"]

    # -----------------------------
    # VARIANT HELPERS
    # -----------------------------

    @property
    def in_stock(self):

        return self.variants.filter(is_active=True, stock__gt=0).exists()

    @property
    def variant_count(self):

        return self.variants.filter(is_active=True).count()

    @property
    def color_variants(self):

        return ProductAttributeValue.objects.filter(
            productvariant__product=self, attribute__name__iexact="color"
        ).distinct()


class ProductImage(BaseModel):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to="products/")

    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="unique_primary_image_per_product",
            )
        ]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductAttribute(BaseModel):

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class ProductAttributeValue(BaseModel):

    attribute = models.ForeignKey(
        ProductAttribute, on_delete=models.CASCADE, related_name="values"
    )

    value = models.CharField(max_length=100)

    color_hex = models.CharField(
        max_length=7, blank=True, null=True, help_text="Example: #FF0000"
    )

    tailwind_color = models.CharField(
        max_length=50, blank=True, null=True, help_text="Example: bg-red-500"
    )

    image = models.ImageField(upload_to="attribute_swatches/", blank=True, null=True)

    class Meta:
        unique_together = ("attribute", "value")
        indexes = [
            models.Index(fields=["attribute"]),
        ]

    def __str__(self):
        return f"{self.attribute.name} : {self.value}"


class ProductVariant(BaseModel):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )

    attributes = models.ManyToManyField(ProductAttributeValue)

    sku = models.CharField(max_length=100, unique=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["product"]),
        ]

    def save(self, *args, **kwargs):

        if not self.sku:
            self.sku = f"SV-{uuid.uuid4().hex[:8].upper()}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"


    @property
    def gallery(self):
        images = list(self.images.all())
        if images:
            return [img.image.url for img in images]
        return [img.image.url for img in self.product.images.all()]


class ProductVariantImage(BaseModel):

    variant = models.ForeignKey(
        "ProductVariant", on_delete=models.CASCADE, related_name="images"
    )

    image = models.ImageField(upload_to="variant_images/")

    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_primary", "id"]
        indexes = [
            models.Index(fields=["variant"]),
        ]

    def __str__(self):
        return f"{self.variant.sku} image"


class Inventory(BaseModel):

    variant = models.OneToOneField(
        ProductVariant, on_delete=models.CASCADE, related_name="inventory"
    )

    stock = models.PositiveIntegerField(default=0)

    low_stock_threshold = models.PositiveIntegerField(default=5)

    def is_available(self, quantity):
        return self.stock >= quantity

    def reduce_stock(self, quantity):

        if quantity > self.stock:
            raise ValueError("Not enough stock available")

        self.stock -= quantity
        self.save()

    def __str__(self):
        return f"{self.variant.sku} Stock: {self.stock}"


class ProductView(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="views")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    session_id = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"View: {self.product.name}"
