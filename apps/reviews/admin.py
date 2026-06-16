from django.contrib import admin
from .models import Review, ReviewVote, ReviewMedia


# =========================================================
# REVIEW MEDIA INLINE
# =========================================================

class ReviewMediaInline(admin.TabularInline):

    model = ReviewMedia
    extra = 0
    fields = (
        "file",
        "media_type",
        "sort_order",
        "is_approved",
        "created_at",
    )
    readonly_fields = ("created_at",)
    ordering = ("sort_order",)


# =========================================================
# REVIEW ADMIN
# =========================================================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "product",
        "user",
        "rating",
        "is_verified_purchase",
        "is_featured",
        "is_approved",
        "media_count",
        "helpful_votes",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_verified_purchase",
        "is_featured",
        "is_approved",
        "created_at",
    )

    search_fields = (
        "product__name",
        "user__email",
        "title",
        "comment",
    )

    ordering = ("-created_at",)

    list_select_related = (
        "product",
        "user",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "helpful_votes",
        "not_helpful_votes",
        "total_votes",
    )

    actions = (
        "approve_reviews",
        "unapprove_reviews",
        "feature_reviews",
        "unfeature_reviews",
    )

    inlines = [ReviewMediaInline]

    fieldsets = (

        ("Review Info", {
            "fields": (
                "product",
                "user",
                "rating",
                "title",
                "comment",
            )
        }),

        ("Flags", {
            "fields": (
                "is_verified_purchase",
                "is_approved",
                "is_featured",
            )
        }),

        ("Votes", {
            "fields": (
                "helpful_votes",
                "not_helpful_votes",
                "total_votes",
            )
        }),

        ("Dates", {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),

    )

    # -----------------------------------------------------
    # ACTIONS
    # -----------------------------------------------------

    @admin.action(description="Approve selected reviews")
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Unapprove selected reviews")
    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)

    @admin.action(description="Feature selected reviews")
    def feature_reviews(self, request, queryset):
        queryset.update(is_featured=True)

    @admin.action(description="Remove featured status")
    def unfeature_reviews(self, request, queryset):
        queryset.update(is_featured=False)


# =========================================================
# REVIEW VOTE ADMIN
# =========================================================

@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):

    list_display = (
        "review",
        "user",
        "is_helpful",
        "created_at",
    )

    list_filter = (
        "is_helpful",
    )

    search_fields = (
        "review__product__name",
        "user__email",
    )

    list_select_related = (
        "review",
        "user",
    )


# =========================================================
# REVIEW MEDIA ADMIN
# =========================================================

@admin.register(ReviewMedia)
class ReviewMediaAdmin(admin.ModelAdmin):

    list_display = (
        "review",
        "media_type",
        "is_approved",
        "sort_order",
        "created_at",
    )

    list_filter = (
        "media_type",
        "is_approved",
    )

    search_fields = (
        "review__product__name",
    )

    list_select_related = (
        "review",
    )

    ordering = ("sort_order",)