from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import BaseModel
from apps.products.models import Product


User = settings.AUTH_USER_MODEL


# =========================================================
# REVIEW
# =========================================================

class Review(BaseModel):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    title = models.CharField(
        max_length=255,
        blank=True
    )

    comment = models.TextField(
        blank=True
    )

    is_verified_purchase = models.BooleanField(default=False)

    is_approved = models.BooleanField(default=True)

    # future moderation
    is_featured = models.BooleanField(default=False)

    class Meta:

        unique_together = ("product", "user")

        indexes = [
            models.Index(fields=["product"]),
            models.Index(fields=["user"]),
            models.Index(fields=["product", "rating"]),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating}⭐"

    @property
    def short_comment(self):
        return self.comment[:120]

    @property
    def helpful_votes(self):
        return self.votes.filter(is_helpful=True).count()

    @property
    def not_helpful_votes(self):
        return self.votes.filter(is_helpful=False).count()

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def media_count(self):
        return self.media.count()

    
# =========================================================
# REVIEW MEDIA (Images / Videos)
# =========================================================

class ReviewMedia(BaseModel):

    IMAGE = "image"
    VIDEO = "video"

    MEDIA_TYPE_CHOICES = [
        (IMAGE, "Image"),
        (VIDEO, "Video"),
    ]

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="media"
    )

    file = models.FileField(
        upload_to="review_media/"
    )

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES
    )

    sort_order = models.PositiveIntegerField(
        default=0
    )

    is_approved = models.BooleanField(
        default=True
    )

    class Meta:

        ordering = ["sort_order", "created_at"]

        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["media_type"]),
        ]

    def __str__(self):
        return f"{self.review.id} - {self.media_type}"


# =========================================================
# REVIEW VOTES
# =========================================================

class ReviewVote(BaseModel):

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="votes"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    is_helpful = models.BooleanField()

    class Meta:

        unique_together = ("review", "user")

        indexes = [
            models.Index(fields=["review"]),
            models.Index(fields=["user"]),
            models.Index(fields=["review", "is_helpful"]),
        ]

    def __str__(self):
        label = "Helpful" if self.is_helpful else "Not Helpful"
        return f"{self.review.id} - {label}"
    
