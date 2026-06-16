from django.db import models
from django.utils import timezone
from django.utils.html import format_html

from .base import BaseModel


class Banner(BaseModel):

    LOCATION_CHOICES = [
        ("home_hero", "Homepage Hero"),
        ("home_middle", "Homepage Middle"),
        ("category_top", "Category Top"),
    ]

    title = models.CharField(max_length=255)

    subtitle = models.CharField(
        max_length=255,
        blank=True
    )

    image = models.ImageField(upload_to="banners/")

    mobile_image = models.ImageField(
        upload_to="banners/mobile/",
        blank=True,
        null=True
    )

    link = models.URLField(blank=True)

    button_text = models.CharField(
        max_length=50,
        blank=True
    )

    location = models.CharField(
        max_length=50,
        choices=LOCATION_CHOICES,
        default="home_hero"
    )

    priority = models.PositiveIntegerField(default=0)

    start_date = models.DateTimeField(blank=True, null=True)

    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-priority"]

    def is_active_now(self):

        now = timezone.now()

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True

    def preview(self):

        if self.image:
            return format_html(
                '<img src="{}" width="200"/>',
                self.image.url
            )

        return "No Image"

    preview.short_description = "Preview"

    def __str__(self):
        return self.title