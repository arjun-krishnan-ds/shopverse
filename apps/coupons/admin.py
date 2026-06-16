from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):

    # =====================================================
    # LIST DISPLAY
    # =====================================================

    list_display = (
        "code",
        "discount_type",
        "discount_value",
        "min_cart_value",
        "max_discount",
        "valid_from",
        "valid_to",
        "is_active",
        "usage_status",
    )

    list_filter = (
        "discount_type",
        "is_active",
        "valid_from",
        "valid_to",
    )

    search_fields = (
        "code",
    )

    readonly_fields = (
        "used_count",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    # =====================================================
    # FIELDSETS
    # =====================================================

    fieldsets = (

        ("Coupon Info", {
            "fields": (
                "code",
                "discount_type",
                "discount_value",
                "max_discount",
            )
        }),

        ("Cart Rules", {
            "fields": (
                "min_cart_value",
            )
        }),

        ("Validity", {
            "fields": (
                "valid_from",
                "valid_to",
                "is_active",
            )
        }),

        ("Usage Tracking", {
            "fields": (
                "used_count",
            )
        }),

        ("System", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),

    )

    # =====================================================
    # STATUS BADGE
    # =====================================================

    def usage_status(self, obj):

        now = timezone.now()

        if not obj.is_active:
            return format_html(
                '<span style="color:red;font-weight:bold;">Inactive</span>'
            )

        if obj.valid_to and obj.valid_to < now:
            return format_html(
                '<span style="color:red;">Expired</span>'
            )

        if obj.valid_from and obj.valid_from > now:
            return format_html(
                '<span style="color:orange;">Scheduled</span>'
            )

        return format_html(
            '<span style="color:green;">Active</span>'
        )

    usage_status.short_description = "Status"