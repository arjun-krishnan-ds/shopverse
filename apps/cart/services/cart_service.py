from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.products.models import ProductVariant
from apps.cart.models import Cart, CartItem


class CartService:
    """
    Central service for all cart operations.

    Keeps business logic out of views.
    """

    @staticmethod
    def get_cart(user):
        """
        Get or create cart for authenticated user.
        """
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    @transaction.atomic
    def add_to_cart(user, variant_id, quantity=1):
        """
        Add product variant to cart.

        Handles:
        - duplicate items
        - stock validation
        """

        variant = get_object_or_404(ProductVariant, id=variant_id)

        if variant.stock <= 0:
            raise ValueError("Product out of stock")

        cart = CartService.get_cart(user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
        )

        new_quantity = cart_item.quantity + quantity if not created else quantity

        if new_quantity > variant.stock:
            raise ValueError("Not enough stock available")

        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity"])

        return cart_item

    @staticmethod
    @transaction.atomic
    def remove_item(user, item_id):
        """
        Remove item from cart.
        """

        cart = CartService.get_cart(user)

        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        item.delete()

    @staticmethod
    @transaction.atomic
    def update_quantity(user, item_id, quantity):
        """
        Update cart item quantity.
        """

        cart = CartService.get_cart(user)

        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        if quantity <= 0:
            item.delete()
            return None

        if quantity > item.variant.stock:
            raise ValueError("Not enough stock")

        item.quantity = quantity
        item.save(update_fields=["quantity"])

        return item

    @staticmethod
    def clear_cart(user):
        """
        Remove all cart items.
        """

        cart = CartService.get_cart(user)

        cart.items.all().delete()


    @staticmethod
    def get_session_cart(request):
        """
        Returns session cart dictionary.
        """
        return request.session.setdefault("cart", {})


    @staticmethod
    def add_to_session_cart(request, variant_id, quantity=1):
        """
        Add item to guest session cart.
        """

        cart = CartService.get_session_cart(request)

        variant_id = str(variant_id)

        if variant_id in cart:
            cart[variant_id] += quantity
        else:
            cart[variant_id] = quantity

        request.session.modified = True

        return cart


    @staticmethod
    def merge_session_cart(request, user):
        """
        Merge session cart into user cart after login.
        """

        session_cart = request.session.get("cart")

        if not session_cart:
            return

        for variant_id, quantity in session_cart.items():

            try:
                CartService.add_to_cart(user, variant_id, quantity)
            except Exception:
                pass

        del request.session["cart"]
