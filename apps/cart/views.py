from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import redirect
from .models import CartItem
from .utils import get_or_create_cart, add_product_to_cart


# ============================================
# CART DETAIL PAGE
# ============================================

def cart_detail_view(request):
    cart = get_or_create_cart(request, request.user)
    cart_items = cart.items.select_related(
        "variant",
        "variant__product",
        "variant__product__brand",
        "variant__product__category",
    ).prefetch_related(
        "variant__images",
        "variant__product__images",
        "variant__attributes__attribute",
    )

    subtotal = sum(item.total_price for item in cart_items)

    session_coupon = request.session.get("coupon_code", "")
    session_discount = request.session.get("discount", 0)

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "subtotal": subtotal,
        "session_coupon": session_coupon,
        "session_discount": session_discount,
    }
    return render(request, "pages/cart/cart_detail.html", context)


# ============================================
# CART JSON (FOR CART DRAWER + ALPINE STORE)
# ============================================

@require_GET
def cart_json_view(request):
    cart = get_or_create_cart(request, request.user)

    items = []

    for item in cart.items.select_related("variant__product"):
        product = item.variant.product

        # Safe image URL — handles Cloudinary and local media
        image = None
        try:
            if product.images.exists():
                img = product.images.first().image.url
                if img and (img.startswith("http") or img.startswith("/media/")):
                    image = img
        except Exception:
            image = None

        items.append({
            "id":         item.id,
            "variant_id": item.variant.id,       # ← required by cartStore.hasVariant()
            "name":       product.name,
            "variant":    str(item.variant) if item.variant else "",
            "price":      float(item.variant.price),
            "qty":        item.quantity,
            "image":      image,
            "slug":       product.slug,
        })

    subtotal = sum(i["price"] * i["qty"] for i in items)

    return JsonResponse({
        "success":  True,
        "items":    items,
        "subtotal": subtotal,
    })


# ============================================
# ADD TO CART
# ============================================

@require_POST
def add_to_cart_view(request, variant_id):
    try:
        quantity = int(request.POST.get("quantity", 1))
        if quantity <= 0:
            quantity = 1
    except (TypeError, ValueError):
        quantity = 1

    try:
        add_product_to_cart(
            request=request,
            variant_id=variant_id,
            quantity=quantity
        )
    except Exception:
        return JsonResponse({
            "success": False,
            "error":   "Failed to add product"
        }, status=400)

    cart = get_or_create_cart(request, request.user)
    cart_items = cart.items.select_related("variant__product")

    cart_count    = sum(item.quantity    for item in cart_items)
    cart_subtotal = sum(item.total_price for item in cart_items)

    # AJAX response (Alpine cartStore)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success":      True,
            "cart_count":   cart_count,
            "cart_subtotal": float(cart_subtotal),
            "cart_total":   float(cart_subtotal),
        })

    # Non-JS fallback
    messages.success(request, "Product added to cart")
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ============================================
# UPDATE CART ITEM (AJAX)
# ============================================

@require_POST
def update_cart_item_view(request):
    item_id = request.POST.get("item_id")

    try:
        quantity = int(request.POST.get("qty", 1))
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "error": "Invalid quantity"}, status=400)

    cart = get_or_create_cart(request, request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()

    cart_items    = cart.items.select_related("variant__product")
    subtotal      = sum(item.total_price for item in cart_items)
    cart_count    = sum(item.quantity    for item in cart_items)

    return JsonResponse({
        "success":       True,
        "cart_count":    cart_count,
        "cart_subtotal": float(subtotal),
    })

# ============================================
# REMOVE ITEM
# ============================================

@require_POST
def remove_from_cart_view(request):
    item_id = request.POST.get("item_id")

    cart = get_or_create_cart(request, request.user)

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart,
    )

    item.delete()

    cart_items = cart.items.select_related(
        "variant__product"
    )

    subtotal = sum(
        item.total_price
        for item in cart_items
    )

    cart_count = sum(
        item.quantity
        for item in cart_items
    )

    # AJAX request
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "cart_count": cart_count,
            "cart_subtotal": float(subtotal),
        })

    # Normal form submit
    return redirect("cart:cart_detail")