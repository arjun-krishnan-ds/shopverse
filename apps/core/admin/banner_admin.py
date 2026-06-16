from django.contrib import admin
from apps.core.models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "location",
        "priority",
        "is_active",
        "preview",
        "created_at",
    )

    list_filter = (
        "location",
        "is_active",
    )

    search_fields = (
        "title",
    )

    readonly_fields = ("preview",)

    ordering = ("-priority",)