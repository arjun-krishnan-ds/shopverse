from django.db.models import Count

from apps.products.models import Product
from apps.products.models import ProductView
from apps.orders.models import OrderItem


class RecommendationService:

    @staticmethod
    def recently_viewed(session_id, limit=6):
        """
        Products recently viewed by a user session.
        """

        views = (
            ProductView.objects
            .filter(session_id=session_id)
            .select_related("product")
            .order_by("-created_at")
        )

        product_ids = []

        for view in views:
            if view.product_id not in product_ids:
                product_ids.append(view.product_id)

        return Product.objects.filter(id__in=product_ids)[:limit]

    @staticmethod
    def trending_products(limit=8):
        """
        Most viewed products in the system.
        """

        trending = (
            ProductView.objects
            .values("product")
            .annotate(total_views=Count("id"))
            .order_by("-total_views")[:limit]
        )

        product_ids = [item["product"] for item in trending]

        return Product.objects.filter(id__in=product_ids)

    @staticmethod
    def top_selling_products(limit=8):
        """
        Best selling products.
        """

        best_sellers = (
            OrderItem.objects
            .values("product_variant__product")
            .annotate(total_sold=Count("id"))
            .order_by("-total_sold")[:limit]
        )

        product_ids = [
            item["product_variant__product"] for item in best_sellers
        ]

        return Product.objects.filter(id__in=product_ids)

    @staticmethod
    def customers_also_bought(product_id, limit=6):
        """
        Products purchased with the same product.
        """

        related_orders = (
            OrderItem.objects
            .filter(product_variant__product_id=product_id)
            .values_list("order_id", flat=True)
        )

        related_products = (
            OrderItem.objects
            .filter(order_id__in=related_orders)
            .exclude(product_variant__product_id=product_id)
            .values("product_variant__product")
            .annotate(total=Count("id"))
            .order_by("-total")[:limit]
        )

        product_ids = [
            item["product_variant__product"] for item in related_products
        ]

        return Product.objects.filter(id__in=product_ids)

    # =========================================================
    # 🔥 NEW: MAIN ENTRY POINT (FIXES YOUR ERROR)
    # =========================================================

    @staticmethod
    def get_recommendations_for_user(user, session_id=None, limit=8):
        """
        Unified recommendation method for product listing page.
        """

        # 1. Try recently viewed (best signal)
        if session_id:
            recent = RecommendationService.recently_viewed(session_id, limit)
            if recent.exists():
                return recent

        # 2. Try top selling
        top_selling = RecommendationService.top_selling_products(limit)
        if top_selling.exists():
            return top_selling

        # 3. Try trending
        trending = RecommendationService.trending_products(limit)
        if trending.exists():
            return trending

        # 4. Final fallback (never fail)
        return Product.objects.filter(is_active=True).order_by("-created_at")[:limit]