from django.contrib import admin
from .models import DeliveryRule


@admin.register(DeliveryRule)
class DeliveryRuleAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "min_order_value",
        "delivery_fee",
        "priority",
        "is_active",
    ]

    list_filter = ["is_active"]

    ordering = ["priority"]