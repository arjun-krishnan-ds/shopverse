import logging

import stripe

from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.urls import reverse

from apps.cart.models import Cart
from apps.accounts.models import Address
from apps.delivery.services.delivery_service import DeliveryService
from apps.delivery.services.eta_service import ETAService
from apps.payments.services.payment_service import PaymentService
from apps.cart.utils import get_or_create_cart

from .models import Order
from .exceptions import InsufficientStock
from .services.order_service import OrderService
from .services.checkout_service import CheckoutService
from .services.invoice_service import InvoiceService

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)


@login_required(login_url="/accounts/login/")
def create_checkout_session(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")
    messages.error(request, "Direct checkout session is disabled.")
    return redirect("cart:cart_detail")


# =========================================================
# CHECKOUT PAGE — ADDRESS + PAYMENT SELECTION
# =========================================================

@login_required(login_url="/accounts/login/")
def checkout_page(request):

    # =====================================================
    # CART
    # =====================================================

    cart = get_or_create_cart(request, request.user)

    cart_items = (
        cart.items
        .select_related(
            "variant",
            "variant__product",
        )
        .prefetch_related(
            "variant__images",
            "variant__product__images",
            "variant__attributes__attribute",
        )
    )

    # =====================================================
    # EMPTY CART
    # =====================================================

    if not cart_items.exists():

        # Prevent re-submit after successful order
        last_order_id = request.GET.get("order_id")

        if last_order_id:

            return redirect(
                f"/orders/success/?order_id={last_order_id}"
            )

        return redirect("cart:cart_detail")

    # =====================================================
    # ADDRESSES
    # =====================================================

    addresses = (
        Address.objects
        .filter(user=request.user)
        .order_by("-is_default", "-id")
    )

    # =====================================================
    # SUBTOTAL
    # =====================================================

    subtotal = sum(
        (
            item.total_price
            for item in cart_items
        ),
        Decimal("0.00")
    )

    # =====================================================
    # DISCOUNT
    # =====================================================

    try:

        discount = Decimal(
            str(
                request.session.get(
                    "discount",
                    "0.00"
                )
            )
        )

    except (InvalidOperation, TypeError):

        discount = Decimal("0.00")

    # =====================================================
    # DELIVERY FEE
    # =====================================================

    delivery_fee = (
        DeliveryService.calculate_delivery(
            subtotal
        )
    )

    # =====================================================
    # TOTAL
    # =====================================================

    total = (
        subtotal
        - discount
        + delivery_fee
    )

    if total < Decimal("0.00"):
        total = Decimal("0.00")

    # =====================================================
    # POST — PLACE ORDER
    # =====================================================

    if request.method == "POST":

        address_id = request.POST.get(
            "address_id"
        )

        payment_method = request.POST.get(
            "payment_method",
            "cod"
        )

        # =============================================
        # COD ELIGIBILITY GUARD
        # Orders above ₹5,000 must be paid online.
        # Prevents tampered POST requests bypassing
        # the frontend restriction.
        # =============================================

        COD_LIMIT = Decimal("5000.00")

        if payment_method == "cod" and total > COD_LIMIT:
            messages.error(
                request,
                "Cash on Delivery is only available for orders up to ₹5,000. "
                "Please choose online payment to proceed."
            )
            return redirect("checkout_page")

        if not address_id:

            messages.error(
                request,
                "Please select a delivery address."
            )

            return redirect("checkout_page")

        address = get_object_or_404(
            Address,
            id=address_id,
            user=request.user
        )

        try:

            # =============================================
            # CART FINGERPRINT
            # A sorted snapshot of variant_id:qty used to
            # detect whether the cart changed between
            # checkout attempts. If it hasn't, we can
            # safely reuse an existing PENDING Stripe order
            # instead of creating a duplicate.
            # =============================================

            cart_items_qs = get_or_create_cart(
                request, request.user
            ).items.select_related("variant")

            cart_fingerprint = ":".join(
                f"{item.variant_id},{item.quantity}"
                for item in cart_items_qs.order_by("variant_id")
            )

            # =============================================
            # REUSE PENDING STRIPE ORDER (if applicable)
            # Prevents duplicate orders when the customer
            # clicks Back from Stripe and submits again.
            # =============================================

            order = None

            if payment_method == "stripe":

                pending_order_id = request.session.get(
                    "pending_stripe_order_id"
                )
                stored_fingerprint = request.session.get(
                    "pending_stripe_cart_fingerprint"
                )

                if pending_order_id and stored_fingerprint == cart_fingerprint:
                    try:
                        candidate = Order.objects.get(
                            id=pending_order_id,
                            user=request.user,
                            status=Order.Status.PENDING,
                        )
                        # Reuse — update address in case they changed it
                        candidate.address = address
                        candidate.save(update_fields=["address"])
                        order = candidate

                    except Order.DoesNotExist:
                        # Order was cancelled or doesn't exist — fall through
                        # to create a new one below
                        pass

                elif pending_order_id:
                    # Cart changed or fingerprint mismatch — cancel the stale order
                    try:
                        stale = Order.objects.get(
                            id=pending_order_id,
                            user=request.user,
                            status=Order.Status.PENDING,
                        )
                        stale.status = Order.Status.CANCELLED
                        stale.save(update_fields=["status"])
                    except Order.DoesNotExist:
                        pass

            # =============================================
            # CREATE ORDER (only if not reusing)
            # =============================================

            if order is None:
                order = (
                    CheckoutService
                    .create_order_from_cart(
                        user=request.user,
                        address=address,
                        request=request,
                    )
                )

            # =============================================
            # SAVE ORDER SNAPSHOT
            # =============================================

            order.payment_method = (
                payment_method
            )

            order.discount_amount = (
                discount
            )

            order.shipping_cost = (
                delivery_fee
            )

            order.total_amount = total

            if request.session.get(
                "coupon_code"
            ):

                order.coupon_code = (
                    request.session.get(
                        "coupon_code"
                    )
                )

            order.save(
                update_fields=[
                    "payment_method",
                    "discount_amount",
                    "shipping_cost",
                    "total_amount",
                    "coupon_code",
                ]
            )

            # =============================================
            # CLEAR SESSION
            # =============================================

            request.session.pop(
                "coupon_code",
                None
            )

            request.session.pop(
                "discount",
                None
            )

            # =============================================
            # STRIPE PAYMENT
            # =============================================

            if (
                payment_method == "stripe"
                and getattr(
                    settings,
                    "STRIPE_SECRET_KEY",
                    None,
                )
            ):

                stripe.api_key = (
                    settings.STRIPE_SECRET_KEY
                )

                try:

                    payment_url = (
                        PaymentService
                        .create_payment(
                            order=order,
                            gateway="stripe",
                        )
                    )

                    if payment_url:

                        # Store pending order in session so that if
                        # the customer clicks Back and resubmits we
                        # reuse this order rather than creating a new one.
                        request.session["pending_stripe_order_id"] = order.id
                        request.session["pending_stripe_cart_fingerprint"] = cart_fingerprint

                        return redirect(
                            payment_url
                        )

                except Exception as stripe_error:
                    logger.error(f"STRIPE SESSION CREATION FAILED for order {order.id}: {stripe_error}")
                    # Cancel the dangling pending order
                    try:
                        order.status = Order.Status.CANCELLED
                        order.save(update_fields=["status"])
                    except Exception:
                        pass
                    messages.error(request, "Unable to initialize payment. Please try again.")
                    return redirect("checkout_page")

            # =============================================
            # COD SUCCESS — clear pending session keys
            # =============================================

            request.session.pop("pending_stripe_order_id", None)
            request.session.pop("pending_stripe_cart_fingerprint", None)

            # =============================================
            # SUCCESS REDIRECT
            # =============================================

            success_url = (
                reverse("order_success")
                + f"?order_id={order.id}"
            )

            return redirect(success_url)

        # =================================================
        # STOCK ERROR
        # =================================================

        except InsufficientStock as e:

            messages.error(
                request,
                str(e)
            )

            return redirect("cart:cart_detail")

        # =================================================
        # GENERAL ERROR
        # =================================================

        except Exception as e:

            logger.error(
                f"CHECKOUT ERROR: {str(e)}"
            )

            messages.error(
                request,
                f"Checkout failed: {str(e)}"
            )

            return redirect(
                "checkout_page"
            )

    # =====================================================
    # CONTEXT
    # =====================================================

    context = {
        "cart": cart,
        "cart_items": cart_items,
        "addresses": addresses,
        "subtotal": subtotal,
        "discount": discount,
        "delivery_fee": delivery_fee,
        "total": total,
        "cod_allowed": total <= Decimal("5000.00"),
    }

    return render(
        request,
        "pages/orders/checkout.html",
        context,
    )

# =========================================================
# ORDER SUCCESS PAGE
# =========================================================

@login_required
def order_success(request):

    order_id = request.GET.get("order_id")

    # =====================================================
    # ORDER ID REQUIRED
    # =====================================================

    if not order_id:

        messages.error(
            request,
            "Invalid order."
        )

        return redirect("cart:cart_detail")

    # =====================================================
    # FETCH ORDER
    # =====================================================

    try:

        order = Order.objects.get(
            id=order_id,
            user=request.user
        )

    except Order.DoesNotExist:

        messages.error(
            request,
            "Order not found."
        )

        return redirect("cart:cart_detail")

    # =====================================================
    # STRIPE PAYMENT VERIFICATION
    # =====================================================
    # The webhook may arrive a few seconds after Stripe redirects
    # the customer. If the order is not yet PAID, redirect to the
    # order list with an informational message rather than showing
    # a false "success" screen.

    PAID_STATUSES = (
        Order.Status.PAID,
        Order.Status.PROCESSING,
        Order.Status.SHIPPED,
        Order.Status.OUT_FOR_DELIVERY,
        Order.Status.DELIVERED,
    )

    if (
        order.payment_method == "stripe"
        and order.status not in PAID_STATUSES
    ):
        messages.info(
            request,
            "Your payment is being verified. "
            "We'll update your order status shortly — "
            "you'll receive a confirmation email once it's confirmed."
        )
        return redirect("user_orders")

    # Add after the stripe check:
    if order.status == Order.Status.CANCELLED:
        messages.error(request, "This order has been cancelled.")
        return redirect("user_orders")
    # =====================================================
    # RENDER SUCCESS PAGE
    # =====================================================

    # Payment confirmed — clear the pending order session
    # keys so the next purchase starts completely fresh.
    request.session.pop("pending_stripe_order_id", None)
    request.session.pop("pending_stripe_cart_fingerprint", None)

    return render(
        request,
        "pages/orders/order_success.html",
        {
            "order": order
        }
    )

@login_required
def user_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )
    return render(request, "pages/orders/order_list.html", {"orders": orders})


def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    eta = ETAService.estimate(order)
    shipment = getattr(order, "shipment", None)
    payment = getattr(order, "payment", None)

    progress_width = {
        "pending": 0,
        "paid": 25,
        "processing": 25,
        "shipped": 50,
        "out_for_delivery": 75,
        "delivered": 100,
    }.get(order.status, 0)

    delivery_info = {
        "estimated_delivery": order.estimated_delivery,
        "shipped_at": order.shipped_at,
        "status": order.status,
        "tracking_id": order.tracking_id,
        "courier_name": order.courier_name,
        "can_cancel": order.can_be_cancelled,
        "status_steps": [
            {"step": "Order Placed", "status": "pending", "icon": "✓", "active": True},
            {
                "step": "Processing",
                "status": "processing",
                "icon": "⏳",
                "active": order.status
                in ["processing", "shipped", "out_for_delivery", "delivered"],
            },
            {
                "step": "Shipped",
                "status": "shipped",
                "icon": "📦",
                "active": order.status in ["shipped", "out_for_delivery", "delivered"],
            },
            {
                "step": "Out for Delivery",
                "status": "out_for_delivery",
                "icon": "🚗",
                "active": order.status in ["out_for_delivery", "delivered"],
            },
            {
                "step": "Delivered",
                "status": "delivered",
                "icon": "✓",
                "active": order.status == "delivered",
            },
        ],
    }

    context = {
        "order": order,
        "delivery_info": delivery_info,
        "eta": eta,
        "shipment": shipment,
        "payment": payment,
        "progress_width": progress_width,
    }
    return render(request, "pages/orders/order_detail.html", context)


@login_required
@require_POST
def cancel_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    try:
        OrderService.cancel_order(order)
        messages.success(request, "Order cancelled successfully.")
    except Exception as e:
        messages.error(request, str(e))
    return redirect("order_detail", order_number=order_number)


@login_required
def download_invoice(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    buffer = InvoiceService.generate_invoice(order)
    return HttpResponse(
        buffer,
        content_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="invoice_{order.id}.pdf"'
        },
    )


def orders_home_view(request):
    if request.user.is_authenticated:
        return redirect("checkout_page")
    return redirect("/accounts/login/?next=/orders/checkout/")


# =========================================================
# PAYMENT CANCELLED
# Called when customer clicks Cancel / Back on Stripe's
# hosted checkout page (via the cancel_url).
# =========================================================

@login_required
def payment_cancelled(request):
    """
    Called when the customer clicks Cancel / Back on Stripe's hosted checkout.

    With the pending-order reuse pattern, we do NOT cancel the order here.
    Instead we leave it PENDING so the checkout POST can reuse it if the
    customer tries again with the same cart.

    The order is only cancelled by the checkout POST if the cart has changed,
    or by the webhook if async payment fails.
    """

    # Clear the pending order session keys so the checkout page
    # re-evaluates cleanly on next visit (reuse logic still applies
    # because the order stays PENDING in the DB — the session lookup
    # is a fast path optimisation, not the only guard).
    # We intentionally keep the keys here so the next checkout POST
    # can still find and reuse the same order — only clear on explicit
    # cart change or successful payment.

    messages.warning(
        request,
        "Payment was cancelled. "
        "Your cart is still saved — complete your order whenever you're ready."
    )

    return redirect("cart:cart_detail")