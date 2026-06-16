from .utils import get_or_create_cart


def cart_item_count(request):
    """
    Global cart context processor.

    Makes cart data available in all templates.

    Available template variables:

    cart_count        -> total quantity of items in cart
    cart_subtotal     -> subtotal before tax/shipping
    cart_total        -> final total
    mini_cart_items   -> latest 5 items for navbar mini-cart
    """

    # Avoid running cart logic on admin or static paths
    if request.path.startswith("/admin"):
        return {}

    try:

        cart = get_or_create_cart(request)

        count = getattr(cart, "total_items", 0)
        subtotal = getattr(cart, "subtotal", 0)
        total = getattr(cart, "total", 0)

        items = cart.items.select_related(
            "variant",
            "variant__product"
        ).order_by("-created_at")[:5]

    except Exception:

        count = 0
        subtotal = 0
        total = 0
        items = []

    return {
        "cart_count": count,
        "cart_subtotal": subtotal,
        "cart_total": total,
        "mini_cart_items": items
    }