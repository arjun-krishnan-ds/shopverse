from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, UserProfile, Address


# =========================================================
# CUSTOM USER ADMIN
# =========================================================

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin for the custom, email-based user model.

    CustomUser has no `username` field, so Django's default
    UserAdmin fieldsets (which reference `username`) must be
    overridden entirely.
    """

    model = CustomUser

    ordering = ("-created_at",)

    list_display = (
        "email",
        "is_staff",
        "is_active",
        "is_verified",
        "is_superuser",
        "created_at",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "is_verified",
        "is_superuser",
    )

    search_fields = ("email",)

    readonly_fields = ("created_at", "updated_at", "last_login", "uuid")

    # Fields shown when editing an existing user
    fieldsets = (
        (None, {
            "fields": ("email", "password")
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "is_verified",
                "groups",
                "user_permissions",
            )
        }),
        ("Important dates", {
            "fields": ("last_login", "created_at", "updated_at")
        }),
        ("System", {
            "fields": ("uuid",)
        }),
    )

    # Fields shown when creating a new user via the admin "Add user" form
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
        ("Permissions", {
            "fields": ("is_active", "is_staff", "is_superuser", "is_verified"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")


# =========================================================
# USER PROFILE
# =========================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "first_name",
        "last_name",
        "phone_number",
    )

    search_fields = (
        "user__email",
        "first_name",
        "last_name",
        "phone_number",
    )

    autocomplete_fields = ("user",)


# =========================================================
# ADDRESS
# =========================================================

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "address_type",
        "city",
        "state",
        "country",
        "is_default",
    )

    list_filter = (
        "address_type",
        "is_default",
        "country",
    )

    search_fields = (
        "user__email",
        "full_name",
        "city",
        "postal_code",
        "phone",
    )

    autocomplete_fields = ("user",)