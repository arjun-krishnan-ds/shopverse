from django.db import transaction
from .models import Cart, CartItem
from apps.products.models import ProductVariant


def get_or_create_cart(request, user=None):

    if user and user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(session_id=session_key)

    return cart


@transaction.atomic
def add_product_to_cart(request, variant_id, quantity=1):

    cart = get_or_create_cart(request, request.user)

    variant = ProductVariant.objects.get(id=variant_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={"quantity": quantity}
    )

    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return cart

@transaction.atomic
def merge_guest_cart_to_user(session_key, user):

    if not session_key:
        return

    try:
        guest_cart = Cart.objects.get(
            session_id=session_key,
            user__isnull=True
        )
    except Cart.DoesNotExist:
        return

    user_cart, created = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():

        cart_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            variant=item.variant,
            defaults={"quantity": item.quantity}
        )

        if not created:
            cart_item.quantity += item.quantity
            cart_item.save()

    guest_cart.delete()