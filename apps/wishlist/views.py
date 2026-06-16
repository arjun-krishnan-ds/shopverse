from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.products.models import Product
from .models import Wishlist
from django.shortcuts import get_object_or_404


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect("product_detail", slug=product.slug)


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    return redirect("wishlist_list")


@login_required
def wishlist_list(request):
    items = Wishlist.objects.filter(user=request.user).select_related(
        "product", "product__brand", "product__category"
    ).prefetch_related("product__images", "product__variants")

    trending_products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:8]

    recent_products = Product.objects.filter(
        is_active=True
    ).order_by("-created_at")[:8]

    return render(request, "pages/wishlist/wishlist.html", {
        "items":             items,
        "trending_products": trending_products,
        "recent_products":   recent_products,
    })


@require_POST
def toggle_wishlist(request, product_id):

    # Cast to int — URL kwargs come in as int already but
    # session may store strings, so normalise both sides.
    product_id = int(product_id)

    product = get_object_or_404(Product, id=product_id)

    # -----------------------------------------
    # GUEST USER → SESSION STORAGE
    # -----------------------------------------
    if not request.user.is_authenticated:

        # Ensure all stored IDs are ints so `in` comparison works
        raw      = request.session.get("wishlist_items", [])
        wishlist = [int(i) for i in raw]

        if product_id in wishlist:
            wishlist.remove(product_id)
            in_wishlist = False
        else:
            wishlist.append(product_id)
            in_wishlist = True

        request.session["wishlist_items"] = wishlist

        return JsonResponse({"in_wishlist": in_wishlist})

    # -----------------------------------------
    # AUTH USER → DATABASE
    # -----------------------------------------
    obj, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        obj.delete()
        return JsonResponse({"in_wishlist": False})

    return JsonResponse({"in_wishlist": True})