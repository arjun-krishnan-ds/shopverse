from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.products.models import Product
from apps.wishlist.models import Wishlist
from .forms import RegisterForm
from .models import Address
from apps.orders.models import Order
from apps.wishlist.models import Wishlist
from apps.cart.utils import get_or_create_cart, merge_guest_cart_to_user


def _merge_guest_wishlist(request, user):
    """
    Merge guest-session wishlist items into the authenticated
    user's wishlist.

    Safe to call after login() — wishlist items are stored in
    request.session's data dict (under "wishlist_items"), which
    Django's cycle_key() preserves (it copies session data to
    the new session id), unlike DB-row lookups keyed by the
    session id string (see merge_guest_cart_to_user for that
    case).
    """

    wishlist_items = request.session.get("wishlist_items", [])

    if not wishlist_items:
        return

    for product_id in wishlist_items:

        product = Product.objects.filter(id=product_id).first()

        if product:
            Wishlist.objects.get_or_create(
                user=user,
                product=product
            )

    # clear session wishlist after merge
    del request.session["wishlist_items"]


def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            # =====================================================
            # CAPTURE GUEST SESSION KEY BEFORE login()
            # =====================================================
            # django.contrib.auth.login() calls
            # request.session.cycle_key(), which rotates the
            # session id for security. The guest Cart row (if
            # any) is stored under the CURRENT (pre-login)
            # session id, so we must capture it now or the
            # later lookup will never find it.
            guest_session_key = request.session.session_key

            user = form.save()

            login(request, user)

            # =====================================================
            # MERGE GUEST CART → USER CART
            # =====================================================
            merge_guest_cart_to_user(guest_session_key, user)

            # =====================================================
            # MERGE GUEST WISHLIST → USER WISHLIST
            # =====================================================
            _merge_guest_wishlist(request, user)

            messages.success(request, "Account created successfully")

            return redirect("/")

    else:
        form = RegisterForm()

    return render(request, "pages/accounts/register.html", {"form": form})



def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:

            # =====================================================
            # CAPTURE GUEST SESSION KEY BEFORE login()
            # =====================================================
            # See register_view for why this must happen before
            # login() — cycle_key() rotates the session id, so
            # the guest Cart row's session_id would otherwise
            # never match request.session.session_key afterwards.
            guest_session_key = request.session.session_key

            login(request, user)

            # =====================================================
            # MERGE GUEST CART → USER CART
            # =====================================================
            merge_guest_cart_to_user(guest_session_key, user)

            # =====================================================
            # MERGE GUEST WISHLIST → USER WISHLIST (SAFE ADDITION)
            # =====================================================
            _merge_guest_wishlist(request, user)

            return redirect("/")

        else:
            messages.error(request, "Invalid credentials")

    return render(request, "pages/accounts/login.html")

def logout_view(request):

    logout(request)

    messages.success(request, "Logged out successfully")

    return redirect("/")


@login_required
def dashboard_view(request):

    recent_orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at")[:5]
    )

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    cart = get_or_create_cart(request, request.user)
    cart_count = sum(item.quantity for item in cart.items.all())

    total_orders = Order.objects.filter(user=request.user).count()

    total_spent = sum(
        o.total_amount for o in Order.objects.filter(
            user=request.user,
            status__in=["paid", "processing", "shipped", "delivered"]
        )
    )

    context = {
        "recent_orders": recent_orders,
        "wishlist_count": wishlist_count,
        "cart_count": cart_count,
        "total_orders": total_orders,
        "total_spent": total_spent,
    }

    return render(request, "pages/accounts/base_dashboard.html", context)


# =========================================================
# ADDRESSES
# =========================================================

@login_required
def address_list_view(request):

    addresses = Address.objects.filter(
    user=request.user
).order_by("-is_default")

    return render(
        request,
        "pages/accounts/address/address_list.html",
        {
            "addresses": addresses
        }
    )


@login_required
def add_address_view(request):

    if request.method == "POST":

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address_line_1 = request.POST.get("address_line_1")
        address_line_2 = request.POST.get("address_line_2")
        city = request.POST.get("city")
        state = request.POST.get("state")
        postal_code = request.POST.get("postal_code")
        country = request.POST.get("country", "India")

        is_default = request.POST.get("is_default") == "on"

        if is_default:
            Address.objects.filter(user=request.user).update(
                is_default=False
            )

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default,
        )

        messages.success(request, "Address added successfully")

        next_url = request.GET.get("next")

        if next_url == "checkout":
            return redirect("checkout_page")

        return redirect("address_list")

    return render(
        request,
        "pages/accounts/address/add_address.html"
    )


@login_required
def edit_address_view(request, id):

    address = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    if request.method == "POST":

        address.full_name = request.POST.get("full_name")
        address.phone = request.POST.get("phone")
        address.address_line_1 = request.POST.get("address_line_1")
        address.address_line_2 = request.POST.get("address_line_2")
        address.city = request.POST.get("city")
        address.state = request.POST.get("state")
        address.postal_code = request.POST.get("postal_code")
        address.country = request.POST.get("country", "India")

        is_default = request.POST.get("is_default") == "on"

        if is_default:
            Address.objects.filter(user=request.user).update(
                is_default=False
            )

        address.is_default = is_default

        address.save()

        messages.success(request, "Address updated successfully")

        return redirect("address_list")

    return render(
        request,
    "pages/accounts/address/add_address.html",
    {
        "address": address,
        "editing": True,
    }
)


@login_required
def delete_address_view(request, id):

    address = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    address.delete()

    messages.success(request, "Address removed successfully")

    return redirect("address_list")


@login_required
def set_default_address_view(request, id):

    address = get_object_or_404(
        Address,
        id=id,
        user=request.user
    )

    Address.objects.filter(user=request.user).update(
        is_default=False
    )

    address.is_default = True
    address.save(update_fields=["is_default"])

    messages.success(request, "Default address updated")

    return redirect("address_list")