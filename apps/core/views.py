import json

from django.shortcuts import render
from django.core.cache import cache
from django.db.models import Avg, Min, Count, Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from apps.products.models import Product, Category
from apps.core.models import Banner
from apps.products.services.recommendation_service import RecommendationService

CACHE_TIMEOUT = 60 * 5


def serialize_products_with_variants(products):
    if not products:
        return []

    serialized = []

    for product in products:
        try:
            variants = product.variants.filter(is_active=True)

            variants_data = [
                {
                    "id": v.id,
                    "price": float(v.price or 0),
                    "stock": int(v.stock or 0),
                    "attributes": {},
                    "images": [],
                }
                for v in variants
            ]

            # Primary image
            primary_image_url = ""

            try:
                primary = product.images.filter(is_primary=True).first()

                if primary and primary.image:
                    primary_image_url = primary.image.url
                else:
                    fallback = product.images.first()
                    if fallback and fallback.image:
                        primary_image_url = fallback.image.url
            except Exception:
                pass

            # Stock
            total_stock = sum(v["stock"] for v in variants_data)

            if total_stock <= 0:
                stock_status = {
                    "status": "out_of_stock",
                    "label": "Out of Stock",
                }
            elif total_stock < 5:
                stock_status = {
                    "status": "low_stock",
                    "label": f"Only {total_stock} left",
                }
            else:
                stock_status = {
                    "status": "in_stock",
                    "label": "In Stock",
                }

            min_price = float(getattr(product, "min_price", 0) or 0)

            review_count = int(getattr(product, "review_count_db", 0) or 0)

            serialized.append(
                {
                    "id": product.id,
                    "name": product.name,
                    "slug": product.slug,
                    # Match product_card expectations
                    "primary_image": (
                        {"image": {"url": primary_image_url}}
                        if primary_image_url
                        else None
                    ),
                    "brand": (
                        {
                            "name": product.brand.name,
                            "slug": product.brand.slug,
                        }
                        if product.brand
                        else None
                    ),
                    "category": (product.category.name if product.category else ""),
                    "min_price": min_price,
                    "avg_rating": float(getattr(product, "avg_rating", 0) or 0),
                    "avg_rating_display": float(getattr(product, "avg_rating", 0) or 0),
                    "review_count": review_count,
                    "review_count_display": review_count,
                    "stock_status": stock_status,
                    "variants_json": json.dumps(variants_data),
                }
            )

        except Exception as e:
            print(f"Serialization error for product {product.id}: {e}")

    return serialized

@ensure_csrf_cookie
def home_view(request):
    cache_key = "home_page_data_v3"
    data = cache.get(cache_key)

    if data:
        return render(request, "pages/home/home.html", data)

    base_products = (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related("images", "variants")
        .annotate(
            avg_rating=Avg(
                "reviews__rating",
                filter=Q(reviews__is_approved=True),
            ),
            review_count_db=Count(
                "reviews",
                filter=Q(reviews__is_approved=True),
            ),
            min_price=Min(
                "variants__price",
                filter=Q(variants__is_active=True),
            ),
        )
    )

    featured_products = base_products.order_by("-created_at")[:8]

    trending_products = (
        RecommendationService.trending_products()
        .select_related("brand", "category")
        .prefetch_related("images", "variants")
        .annotate(
            avg_rating=Avg(
                "reviews__rating",
                filter=Q(reviews__is_approved=True),
            ),
            review_count_db=Count(
                "reviews",
                filter=Q(reviews__is_approved=True),
            ),
            min_price=Min(
                "variants__price",
                filter=Q(variants__is_active=True),
            ),
        )[:8]
    )

    top_rated_products = base_products.order_by("-avg_rating")[:8]

    categories = Category.objects.filter(parent=None).prefetch_related("children")

    now = timezone.now()

    hero_banners = Banner.objects.filter(
        location="home_hero",
        is_active=True,
    ).filter(
        Q(start_date__lte=now) | Q(start_date__isnull=True),
        Q(end_date__gte=now) | Q(end_date__isnull=True),
    )

    try:
        if request.user.is_authenticated:
            recommendations = RecommendationService.get_recommendations_for_user(
                request.user,
                session_id=request.session.session_key,
            )[:8]
        else:
            recommendations = RecommendationService.trending_products()[:8]
    except Exception:
        recommendations = []

    context = {
        "hero_banners": hero_banners,
        "categories": categories,
        "featured_products": serialize_products_with_variants(featured_products),
        "trending_products": serialize_products_with_variants(trending_products),
        "top_rated_products": serialize_products_with_variants(top_rated_products),
        "recommendations": serialize_products_with_variants(recommendations),
    }

    cacheable = {k: v for k, v in context.items() if k not in ("recommendations",)}
    cache.set(cache_key, cacheable, CACHE_TIMEOUT)
    return render(request, "pages/home/home.html", context)
