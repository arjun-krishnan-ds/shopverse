from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Min, Exists, Count, Prefetch, OuterRef
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import IntegrityError
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from .models import (
    Product,
    Category,
    Brand,
    ProductView,ProductVariant
)
from apps.wishlist.models import Wishlist
from apps.reviews.models import Review, ReviewMedia
from .services.recommendation_service import RecommendationService
import json

# =========================================================
# INDUSTRY-STANDARD CONSTANTS
# =========================================================

LOW_STOCK_THRESHOLD = 5  # Below this = "Low Stock"
CACHE_TIMEOUT = 300  # 5 minutes
PRODUCTS_PER_PAGE = 12


# =========================================================
# HELPER FUNCTIONS
# =========================================================


def build_variant_image_data(variant):
    """
    Build image data for a variant.
    Amazon-style: variant images → product images (fallback)
    """
    images = []

    # Get variant-specific images
    variant_images = variant.images.all().order_by("-is_primary")

    if variant_images.exists():
        for img in variant_images:
            try:
                url = img.image.url
                if url:
                    images.append(
                        {
                            "url": url,
                            "alt": f"{variant.product.name} - {variant.sku}",
                            "is_primary": img.is_primary,
                        }
                    )
            except Exception:
                pass

    # Fallback to product images
    if not images:
        product_images = variant.product.images.all().order_by("-is_primary")
        for img in product_images:
            try:
                url = img.image.url
                if url:
                    images.append(
                        {
                            "url": url,
                            "alt": f"{variant.product.name}",
                            "is_primary": img.is_primary,
                        }
                    )
            except Exception:
                pass

    return images


def build_variants_json_for_product(product):
    """
    Build comprehensive variants JSON for product card.
    Returns grouped by attributes for proper color/size selection.
    Amazon-style structure.
    """
    active_variants = product.variants.filter(is_active=True).prefetch_related(
        "attributes__attribute", "images"
    )

    if not active_variants.exists():
        return json.dumps([])

    # Collect all available attribute names
    attribute_names = set()
    for variant in active_variants:
        for attr_value in variant.attributes.all():
            attribute_names.add(attr_value.attribute.name)

    attribute_names = sorted(list(attribute_names))

    # Build variant data with images
    variants_data = []
    for variant in active_variants:
        attrs = {}
        for attr_value in variant.attributes.all():
            attr_name = attr_value.attribute.name
            attrs[attr_name] = {
                "value": attr_value.value,
                "hex": attr_value.color_hex,
                "tailwind": attr_value.tailwind_color,
                "image": attr_value.image.url if attr_value.image else None,
            }

        images = build_variant_image_data(variant)
        primary_image = (
            next((img for img in images if img.get("is_primary")), images[0])
            if images
            else None
        )

        variants_data.append(
            {
                "id": variant.id,
                "sku": variant.sku,
                "price": float(variant.price),
                "stock": int(variant.stock),
                "attributes": attrs,
                "images": images,
                "primary_image": primary_image,
            }
        )

    return json.dumps(variants_data)


def get_stock_status(stock):
    """
    Return industry-standard stock status.
    Amazon/Flipkart style.
    """
    if stock <= 0:
        return {
            "status": "out_of_stock",
            "label": "Out of Stock",
            "class": "bg-red-50 text-red-600",
            "badge": "badge-red",
        }
    elif stock < LOW_STOCK_THRESHOLD:
        return {
            "status": "low_stock",
            "label": f"Only {stock} left",
            "class": "bg-amber-50 text-amber-600",
            "badge": "badge-amber",
        }
    else:
        return {
            "status": "in_stock",
            "label": "In Stock",
            "class": "bg-green-50 text-green-600",
            "badge": "badge-green",
        }


# =========================================================
# PRODUCT LIST VIEW (PRODUCTION-READY)
# =========================================================


def product_list_view(request, category_slug=None):

    query = request.GET.get("q", "").strip()

    # URL category support + query param fallback
    category = category_slug or request.GET.get("category")

    brand = request.GET.get("brand")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    sort = request.GET.get("sort")
    page_number = request.GET.get("page", 1)
    rating = request.GET.get("rating")
    in_stock = request.GET.get("in_stock") == "true"

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    # =====================================================
    # WISHLIST SAFE
    # =====================================================

    user = request.user if request.user.is_authenticated else None

    wishlist_qs = (
        Wishlist.objects.filter(
            user=user,
            product=OuterRef("pk"),
        )
        if user
        else Wishlist.objects.none()
    )

    # =====================================================
    # BASE QUERYSET (OPTIMIZED)
    # =====================================================

    products = (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=(
                    ProductVariant.objects.filter(is_active=True).prefetch_related(
                        "attributes__attribute",
                        "images",
                    )
                ),
            ),
            "reviews",
        )
        .annotate(
            avg_rating=Avg("reviews__rating"),
            total_reviews=Count("reviews", distinct=True),
            min_variant_price=Min("variants__price"),
            is_in_wishlist=Exists(wishlist_qs),
        )
    )

    # =====================================================
    # SEARCH (Full-text search)
    # =====================================================

    if query:

        search_vector = (
            SearchVector("name", weight="A")
            + SearchVector("brand__name", weight="B")
            + SearchVector("category__name", weight="C")
            + SearchVector("description", weight="D")
        )

        search_query = SearchQuery(query)

        products = (
            products.annotate(
                search=search_vector,
                rank=SearchRank(
                    search_vector,
                    search_query,
                ),
            )
            .filter(search=search_query)
            .order_by("-rank")
        )

    # =====================================================
    # FILTERS
    # =====================================================

    if in_stock:
        products = products.filter(variants__stock__gt=0).distinct()

    if category and category != "all":
        products = products.filter(
            Q(category__slug=category) |
            Q(category__parent__slug=category)
        )

    if brand and brand != "all":
        products = products.filter(brand__slug=brand)

    try:

        if min_price:
            products = products.filter(min_variant_price__gte=float(min_price))

    except (ValueError, TypeError):
        pass

    try:

        if max_price:
            products = products.filter(min_variant_price__lte=float(max_price))

    except (ValueError, TypeError):
        pass

    if rating:

        try:
            rating_value = float(rating)

            products = products.filter(avg_rating__gte=rating_value)

        except (ValueError, TypeError):
            pass

    # =====================================================
    # SORTING
    # =====================================================

    if sort == "price_low":

        products = products.order_by("min_variant_price")

    elif sort == "price_high":

        products = products.order_by("-min_variant_price")

    elif sort == "rating":

        products = products.order_by("-avg_rating")

    elif sort == "popular":

        products = products.order_by("-total_reviews")

    elif sort == "newest":

        products = products.order_by("-created_at")

    elif not query:

        products = products.order_by("-created_at")

    products = products.distinct()

    # =====================================================
    # PAGINATION
    # =====================================================

    paginator = Paginator(
        products,
        PRODUCTS_PER_PAGE,
    )

    page_obj = paginator.get_page(page_number)

    # =====================================================
    # PRODUCT CARD DATA ENRICHMENT
    # =====================================================

    for product in page_obj:

        # Price
        product.min_price = (
            getattr(
                product,
                "min_variant_price",
                None,
            )
            or 0
        )

        # Wishlist
        product.in_wishlist = bool(
            getattr(
                product,
                "is_in_wishlist",
                False,
            )
        )

        # Reviews
        product.review_count_display = (
            getattr(
                product,
                "total_reviews",
                0,
            )
            or 0
        )

        product.avg_rating_display = (
            round(product.avg_rating, 1) if product.avg_rating else 0
        )

        # Stock status
        first_variant = product.variants.first()

        if first_variant:

            product.stock_status = get_stock_status(first_variant.stock)

        else:

            product.stock_status = get_stock_status(0)

        # Variants JSON
        try:

            product.variants_json = build_variants_json_for_product(product)

        except Exception:

            product.variants_json = "[]"

        # SAFE PRIMARY IMAGE
        try:

            primary_image = (
                product.images.filter(is_primary=True).first() or product.images.first()
            )

            product.card_primary_image = primary_image

        except Exception:

            product.card_primary_image = None

    # =====================================================
    # AJAX RESPONSE
    # =====================================================

    if is_ajax:

        html = render_to_string(
            "components/products/product_grid.html",
            {
                "page_obj": page_obj,
                "paginator": paginator,
            },
            request=request,
        )

        return JsonResponse(
            {
                "html": html,
                "has_next": page_obj.has_next(),
            }
        )

    # =====================================================
    # FILTER DATA
    # =====================================================

    categories = (
        Category.objects.filter(
            is_active=True,
            parent__isnull=False,
        )
        .exclude(parent__parent__isnull=False)
        .distinct()
    )

    brands = Brand.objects.filter(products__is_active=True).distinct()
    categories_json = json.dumps(
        list(
            categories.values(
                "name",
                "slug",
            )
        )
    )

    brands_json = json.dumps(
        list(
            brands.values(
                "name",
                "slug",
            )
        )
    )

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    recommendations = None

    if request.user.is_authenticated:

        recommendations = (
            RecommendationService.get_recommendations_for_user(
                request.user,
                session_id=request.session.session_key,
            )
            .select_related(
                "brand",
                "category",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "variants",
                    queryset=(
                        ProductVariant.objects.filter(is_active=True).prefetch_related(
                            "attributes__attribute",
                            "images",
                        )
                    ),
                ),
            )
        )[:4]

        for product in recommendations:

            product.in_wishlist = Wishlist.objects.filter(
                user=request.user,
                product=product,
            ).exists()

            product.min_price = (
                getattr(
                    product,
                    "min_variant_price",
                    0,
                )
                or 0
            )

            product.review_count_display = product.reviews.filter(
                is_approved=True
            ).count()

            try:

                product.avg_rating_display = (
                    round(
                        product.average_rating,
                        1,
                    )
                    if product.average_rating
                    else 0
                )

            except Exception:

                product.avg_rating_display = 0

            first_variant = product.variants.first()

            if first_variant:

                product.stock_status = get_stock_status(first_variant.stock)

            else:

                product.stock_status = get_stock_status(0)

            try:

                product.variants_json = build_variants_json_for_product(product)

            except Exception:

                product.variants_json = "[]"

            # SAFE PRIMARY IMAGE
            try:

                primary_image = (
                    product.images.filter(is_primary=True).first()
                    or product.images.first()
                )

                product.card_primary_image = primary_image

            except Exception:

                product.card_primary_image = None

    sort_choices = [
        ("newest", "Newest First"),
        ("price_low", "Price: Low → High"),
        ("price_high", "Price: High → Low"),
        ("rating", "Best Rated"),
        ("popular", "Most Popular"),
    ]

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "page_obj": page_obj,
        "paginator": paginator,
        "products": page_obj,
        "categories": categories or "",
        "brands": brands,
        "categories_json": categories_json,
        "brands_json": brands_json,
        "query": query,
        "selected_category": category or "",
        "selected_brand": brand or "",
        "min_price": min_price or "",
        "max_price": max_price or "",
        "sort": sort or "",
        "rating": rating or "",
        "in_stock": in_stock or "",
        "recommendations": recommendations,
        "sort_choices": sort_choices,
    }

    return render(
        request,
        "pages/products/product_list.html",
        context,
    )


# =========================================================
# PRODUCT DETAIL VIEW (PRODUCTION-READY)
# =========================================================


def product_detail_view(request, slug):

    cache_key = f"product_detail_{slug}"
    product = cache.get(cache_key)

    if not product:
        product = get_object_or_404(
            Product.objects.select_related("brand", "category").prefetch_related(
                "images",
                Prefetch(
                    "variants",
                    queryset=ProductVariant.objects.filter(
                        is_active=True
                    ).prefetch_related("attributes__attribute", "images"),
                ),
                "reviews__user",
            ),
            slug=slug,
            is_active=True,
        )
        cache.set(cache_key, product, CACHE_TIMEOUT)

    # =========================================================
    # SESSION SETUP
    # =========================================================

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    # =========================================================
    # PRODUCT VIEW TRACKING
    # =========================================================

    try:
        if request.user.is_authenticated:
            view_obj, created = ProductView.objects.get_or_create(
                product=product, user=request.user, session_id=session_id
            )
        else:
            view_obj, created = ProductView.objects.get_or_create(
                product=product, session_id=session_id, user=None
            )

        ProductView.objects.filter(product=product, session_id=session_id).exclude(
            id=view_obj.id
        ).delete()

    except IntegrityError:
        pass

    # =========================================================
    # REVIEW SUBMISSION
    # =========================================================

    if request.method == "POST" and request.user.is_authenticated:
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        title = request.POST.get("title")

        if rating:
            review = Review.objects.create(
                product=product,
                user=request.user,
                rating=rating,
                comment=comment or "",
                title=title or "",
                is_approved=False,
            )

            files = request.FILES.getlist("media")
            for f in files:
                ReviewMedia.objects.create(review=review, file=f, is_approved=False)

            html = render_to_string(
                "components/reviews/review_item.html",
                {"review": review},
                request=request,
            )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True, "html": html})

    # =========================================================
    # REVIEWS
    # =========================================================

    reviews_qs = (
        product.reviews.filter(is_approved=True)
        .select_related("user")
        .prefetch_related(
            Prefetch("media", queryset=ReviewMedia.objects.filter(is_approved=True))
        )
        .order_by("-id")
    )

    paginator = Paginator(reviews_qs, 5)
    page_number = request.GET.get("page")
    reviews_page = paginator.get_page(page_number or 1)
    reviews = reviews_page.object_list

    if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.GET.get(
        "page"
    ):
        html = render_to_string(
            "components/reviews/review_list.html", {"reviews": reviews}, request=request
        )
        return JsonResponse({"html": html, "has_more": reviews_page.has_next()})

    # =========================================================
    # REVIEW METRICS
    # =========================================================

    total_reviews = reviews_qs.count()
    avg_rating = reviews_qs.aggregate(avg=Avg("rating"))["avg"] or 0

    rating_distribution = []
    for i in range(5, 0, -1):
        count = reviews_qs.filter(rating=i).count()
        percent = round((count / total_reviews) * 100) if total_reviews > 0 else 0
        rating_distribution.append(
            {
                "rating": i,
                "count": count,
                "percent": int(percent),
                "percent_str": f"{int(percent)}%",
            }
        )

    # =========================================================
    # VARIANTS JSON (PRODUCTION)
    # =========================================================

    product.variants_json = build_variants_json_for_product(product)

    # =========================================================
    # RELATED PRODUCTS
    # =========================================================

    related_products = (
        Product.objects.filter(
            Q(category=product.category) | Q(brand=product.brand), is_active=True
        )
        .exclude(id=product.id)
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).prefetch_related(
                    "attributes__attribute", "images"
                ),
            ),
        )
        .distinct()[:8]
    )

    # =========================================================
    # RECENTLY VIEWED
    # =========================================================

    recent_ids = request.session.get("recent_products", [])
    if product.id in recent_ids:
        recent_ids.remove(product.id)
    recent_ids.append(product.id)
    request.session["recent_products"] = recent_ids[-6:]

    recent_products = (
        Product.objects.filter(id__in=request.session.get("recent_products", []))
        .exclude(id=product.id)
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).prefetch_related(
                    "attributes__attribute", "images"
                ),
            ),
        )
    )[:6]

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    trending_products = RecommendationService.trending_products()
    customers_also_bought = RecommendationService.customers_also_bought(product.id)

    # =========================================================
    # CONTEXT
    # =========================================================

    context = {
        "product": product,
        "reviews": reviews,
        "avg_rating": avg_rating,
        "total_reviews": total_reviews,
        "rating_distribution": rating_distribution,
        "related_products": related_products,
        "recent_products": recent_products,
        "trending_products": trending_products,
        "customers_also_bought": customers_also_bought,
    }

    return render(request, "pages/products/product_detail.html", context)


# =========================================================
# SEARCH PRODUCTS VIEW
# =========================================================


def search_products_view(request):

    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "relevance")

    category_ids = request.GET.getlist("category")
    brand_ids = request.GET.getlist("brand")

    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__name__icontains=query)
        )

    if category_ids and category_ids != "all":
        products = products.filter(category__slug=category_ids)

    if brand_ids and brand_ids != "all":
        products = products.filter(brand__slug=brand_ids)

    if price_min:
        products = products.filter(variants__price__gte=price_min)

    if price_max:
        products = products.filter(variants__price__lte=price_max)

    products = (
        products.select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).prefetch_related(
                    "attributes__attribute", "images"
                ),
            ),
        )
        .annotate(min_price=Min("variants__price"))
        .distinct()
    )

    if sort == "price_low":
        products = products.order_by("min_price")
    elif sort == "price_high":
        products = products.order_by("-min_price")
    elif sort == "newest":
        products = products.order_by("-created_at")

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Enrich products
    for product in page_obj:
        product.min_price = product.min_price or 0
        product.review_count_display = product.reviews.filter(is_approved=True).count()
        product.avg_rating_display = product.average_rating

        first_variant = product.variants.first()
        if first_variant:
            product.stock_status = get_stock_status(first_variant.stock)
        else:
            product.stock_status = get_stock_status(0)

        product.variants_json = build_variants_json_for_product(product)

    categories = Category.objects.all()
    brands = Brand.objects.filter(is_active=True)

    context = {
        "query": query,
        "products": page_obj,
        "sort": sort,
        "categories": categories,
        "brands": brands,
        "selected_categories": category_ids,
        "selected_brands": brand_ids,
    }

    return render(request, "pages/products/product_search.html", context)


# =========================================================
# API: SEARCH AUTOCOMPLETE
# =========================================================


def search_api_view(request):

    query = request.GET.get("q", "").strip()
    products = []

    if query:
        results = (
            Product.objects.filter(
                Q(name__icontains=query) | Q(brand__name__icontains=query),
                is_active=True,
            )
            .select_related("brand")
            .prefetch_related("images", "variants")
            .annotate(min_price=Min("variants__price"))[:8]
        )

        for p in results:
            image = None
            img = p.images.filter(is_primary=True).first() or p.images.first()

            if img:
                image = img.image.url

            products.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "brand": p.brand.name if p.brand else "",
                    "image": image,
                    "price": float(p.min_price) if p.min_price else None,
                }
            )

    return JsonResponse({"products": products})


# =========================================================
# API: QUICK VIEW
# =========================================================


def quickview_product_api(request, product_id):

    product = get_object_or_404(
        Product.objects.select_related("brand", "category").prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).prefetch_related(
                    "attributes__attribute", "images"
                ),
            ),
        ),
        id=product_id,
        is_active=True,
    )

    primary_image = product.primary_image
    image_url = primary_image.image.url if primary_image else None

    # Build variants data
    variants_json = build_variants_json_for_product(product)

    data = {
        "id": product.id,
        "name": product.name,
        "brand": product.brand.name if product.brand else "",
        "price": float(product.lowest_price) if product.lowest_price else None,
        "description": product.description,
        "image": image_url,
        "in_stock": product.in_stock,
        "variants": json.loads(variants_json) if variants_json else [],
    }

    return JsonResponse(data)


# =========================================================
# API: PRODUCTS (FOR GRID LOADING)
# =========================================================


def products_api_view(request):

    products = (
        Product.objects.filter(is_active=True)
        .select_related("brand", "category")
        .prefetch_related(
            "images",
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True).prefetch_related(
                    "attributes__attribute", "images"
                ),
            ),
        )
        .annotate(
            min_price=Min("variants__price"),
            avg_rating=Avg("reviews__rating"),
            review_count_total=Count("reviews__id", distinct=True),
        )
        .distinct()
    )

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    data = []

    for p in page_obj:
        # Images
        images = []
        primary_image = ""

        for img in p.images.all():
            try:
                url = img.image.url
                if url:
                    images.append(url)
                    if img.is_primary and not primary_image:
                        primary_image = url
            except Exception:
                pass

        if not primary_image and images:
            primary_image = images[0]

        # Variants with complete data
        variants = []
        for v in p.variants.all():
            attrs = {}
            for attr_val in v.attributes.all():
                attrs[attr_val.attribute.name] = attr_val.value

            variants.append(
                {
                    "id": v.id,
                    "price": float(v.price),
                    "stock": v.stock,
                    "attributes": attrs,
                }
            )

        # Price
        price = (
            float(p.min_price)
            if p.min_price
            else (variants[0]["price"] if variants else 0)
        )

        # Rating
        rating = round(float(p.avg_rating), 1) if p.avg_rating else None

        data.append(
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "brand": p.brand.name if p.brand else "",
                "category": p.category.name if p.category else "",
                "images": images,
                "image": primary_image,
                "variants": variants,
                "price": price,
                "rating": rating,
                "review_count": p.review_count_total,
            }
        )

    return JsonResponse(
        {
            "products": data,
            "has_next": page_obj.has_next(),
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
        }
    )