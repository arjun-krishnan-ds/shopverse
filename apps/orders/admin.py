from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    readonly_fields = [
        "product_name",
        "sku",
        "quantity",
        "price",
        "total_price",
    ]

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = [
        "order_number",
        "user",
        "status",
        "is_paid",
        "total_amount",
        "created_at",
    ]

    list_filter = [
        "status",
        "is_paid",
        "created_at",
    ]

    search_fields = [
        "order_number",
        "user__email",
        "user__username",
    ]

    readonly_fields = [
        "order_number",
        "total_amount",
        "discount_amount",
        "shipping_cost",
        "created_at",
        "updated_at",
    ]

    ordering = ["-created_at"]

    inlines = [OrderItemInline]

    actions = [
        "mark_as_processing",
        "mark_as_shipped",
        "mark_as_delivered",
        "mark_as_cancelled",
    ]

    # Admin Actions

    @admin.action(description="Mark selected orders as Processing")
    def mark_as_processing(self, request, queryset):
        queryset.update(status="processing")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_as_shipped(self, request, queryset):
        queryset.update(status="shipped")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_as_delivered(self, request, queryset):
        queryset.update(status="delivered")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status="cancelled")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = [
        "order",
        "product_name",
        "sku",
        "quantity",
        "price",
        "total_price",
    ]

    search_fields = [
        "order__order_number",
        "product_name",
        "sku",
    ]