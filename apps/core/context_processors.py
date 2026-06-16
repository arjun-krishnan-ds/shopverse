from apps.products.models import Category
from apps.cart.models import Cart
from apps.wishlist.models import Wishlist


def global_data(request):
    categories = Category.objects.filter(is_active=True)

    cart_count = 0
    wishlist_count = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
         cart_count = cart.total_items
        wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return {
        "categories": categories,
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
    }