from django.contrib import admin
from django.utils.html import format_html
from django.db import transaction

from .models import (
    Category,
    Brand,
    Product,
    ProductImage,
    ProductAttribute,
    ProductAttributeValue,
    ProductVariant,
    ProductVariantImage,
    Inventory
)


# ----------------------------
# CATEGORY
# ----------------------------

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ("thumbnail_preview", "name", "parent", "is_active", "created_at")
    list_filter = ("is_active", "parent", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("large_image_preview", "created_at", "updated_at", "uuid")
    ordering = ("name",)

    fieldsets = (
        ("Category Information", {
            "fields": ("name", "slug", "description", "parent", "image", "large_image_preview")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("System Info", {
            "fields": ("uuid", "created_at", "updated_at")
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:60px;height:60px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "No Image"
    thumbnail_preview.short_description = "Preview"

    def large_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:250px;border-radius:10px;margin-top:10px;" />',
                obj.image.url
            )
        return "No Image"
    large_image_preview.short_description = "Image Preview"


# ----------------------------
# BRAND
# ----------------------------

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):

    list_display = ("logo_preview", "name", "slug", "is_active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    readonly_fields = ("logo_preview", "slug", "uuid", "created_at", "updated_at")

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "slug", "description")
        }),
        ("Media", {
            "fields": ("logo", "logo_preview")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("System", {
            "fields": ("uuid", "created_at", "updated_at")
        }),
    )

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />',
                obj.logo.url
            )
        return "-"
    logo_preview.short_description = "Logo"


# ----------------------------
# PRODUCT IMAGE INLINE
# ----------------------------

class ProductImageInline(admin.TabularInline):

    model = ProductImage
    extra = 3
    max_num = 10
    readonly_fields = ("image_preview",)
    fields = ("image", "is_primary", "image_preview")

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Preview"


# ----------------------------
# VARIANT INLINE
# ----------------------------

class ProductVariantInline(admin.TabularInline):

    model = ProductVariant
    extra = 1
    fields = ("sku", "price", "stock", "is_active")
    readonly_fields = ("sku",)


# ----------------------------
# PRODUCT ADMIN
# ----------------------------

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "thumbnail_preview",
        "name",
        "brand",
        "category",
        "lowest_price_display",
        "in_stock",
        "is_active",
        "created_at"
    )

    prepopulated_fields = {"slug": ("name",)}
    list_filter = ("brand", "category", "is_active")
    search_fields = ("name", "slug")
    autocomplete_fields = ("brand", "category")
    readonly_fields = ("uuid", "created_at", "updated_at")

    fieldsets = (
        ("Product Info", {
            "fields": ("name", "slug", "brand", "category", "description")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("System", {
            "fields": ("uuid", "created_at", "updated_at")
        }),
    )

    inlines = [ProductImageInline, ProductVariantInline]

    def save_formset(self, request, form, formset, change):
        """
        Handle primary image constraint safely.
        Only one image can be primary — enforce this before saving.
        """
        if formset.model == ProductImage:
            instances = formset.save(commit=False)

            with transaction.atomic():
                # Delete marked for deletion
                for obj in formset.deleted_objects:
                    obj.delete()

                # Find if any new instance is marked primary
                has_primary = any(
                    getattr(instance, 'is_primary', False)
                    for instance in instances
                    if not getattr(instance, '_to_delete', False)
                )

                for i, instance in enumerate(instances):
                    # If multiple are marked primary, only keep first one
                    if instance.is_primary and has_primary:
                        if i > 0:
                            # Clear primary on subsequent ones
                            already_primary = any(
                                inst.is_primary for inst in instances[:i]
                            )
                            if already_primary:
                                instance.is_primary = False

                    # Clear existing primary if new primary is being set
                    if instance.is_primary:
                        ProductImage.objects.filter(
                            product=instance.product,
                            is_primary=True
                        ).exclude(pk=instance.pk).update(is_primary=False)

                    instance.save()

                formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)

    def thumbnail_preview(self, obj):
        img = obj.primary_image
        if img:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:6px;" />',
                img.image.url
            )
        return "-"
    thumbnail_preview.short_description = "Image"

    def lowest_price_display(self, obj):
        price = obj.lowest_price
        return f"₹{price}" if price else "-"
    lowest_price_display.short_description = "Price"


# ----------------------------
# ATTRIBUTE
# ----------------------------

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):

    list_display = ("name", "created_at")
    search_fields = ("name",)


# ----------------------------
# ATTRIBUTE VALUE
# ----------------------------

@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):

    list_display = ("attribute", "value", "swatch_preview", "created_at")
    list_filter = ("attribute",)
    search_fields = ("value",)
    readonly_fields = ("swatch_preview",)

    fieldsets = (
        ("Attribute Info", {
            "fields": ("attribute", "value")
        }),
        ("Swatch Settings", {
            "fields": ("color_hex", "tailwind_color", "image", "swatch_preview")
        }),
    )

    def swatch_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;" />',
                obj.image.url
            )
        if obj.color_hex:
            return format_html(
                '<div style="width:30px;height:30px;border-radius:6px;background:{};border:1px solid #ddd;"></div>',
                obj.color_hex
            )
        return "-"
    swatch_preview.short_description = "Swatch"


# ----------------------------
# VARIANT IMAGE INLINE
# ----------------------------

class VariantImageInline(admin.TabularInline):

    model = ProductVariantImage
    extra = 2
    max_num = 8
    readonly_fields = ("image_preview",)
    fields = ("image", "is_primary", "image_preview")

    def image_preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;object-fit:cover;border-radius:6px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Preview"


# ----------------------------
# VARIANT ADMIN
# ----------------------------

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "sku",
        "price",
        "stock",
        "attributes_display",
        "is_active",
        "created_at"
    )

    search_fields = ("sku", "product__name")
    list_filter = ("is_active", "product__brand", "product__category")
    filter_horizontal = ("attributes",)
    autocomplete_fields = ("product",)
    readonly_fields = ("sku", "uuid", "created_at", "updated_at")
    inlines = [VariantImageInline]

    fieldsets = (
        ("Variant Info", {
            "fields": ("product", "sku", "price", "stock", "is_active")
        }),
        ("Attributes", {
            "fields": ("attributes",)
        }),
        ("System", {
            "fields": ("uuid", "created_at", "updated_at")
        }),
    )

    def attributes_display(self, obj):
        return ", ".join(str(attr) for attr in obj.attributes.all())
    attributes_display.short_description = "Attributes"


# ----------------------------
# INVENTORY
# ----------------------------

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = ("variant", "stock", "low_stock_threshold", "created_at")
    search_fields = ("variant__sku",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Inventory", {
            "fields": ("variant", "stock", "low_stock_threshold")
        }),
        ("System", {
            "fields": ("created_at", "updated_at")
        }),
    )