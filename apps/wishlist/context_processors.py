from .models import Wishlist


def wishlist_count(request):

    product_ids = []

    # -----------------------------------------
    # LOGGED IN USER WISHLIST
    # -----------------------------------------
    if request.user.is_authenticated:

        items = Wishlist.objects.filter(user=request.user)

        product_ids = list(items.values_list("product_id", flat=True))

        count = len(product_ids)

    # -----------------------------------------
    # GUEST SESSION WISHLIST
    # -----------------------------------------
    else:

        session_ids = request.session.get("wishlist_items", [])

        product_ids = session_ids

        count = len(session_ids)

    return {
        "wishlist_count": count,
        "wishlist_product_ids": product_ids
    }