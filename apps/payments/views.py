# apps/payments/views.py
"""
Stripe webhook handler and payment-related views.

Webhook responsibilities (checkout.session.completed):
1. Guard against duplicate processing.
2. Mark order PAID + set is_paid = True.
3. Deduct stock for each order item (only here, never in CheckoutService).
4. Clear the user's cart.
5. Record the Payment object.
6. Fire async confirmation email.

Webhook responsibilities (checkout.session.async_payment_failed):
1. Mark order CANCELLED (only if not already PAID).
2. Record the failed Payment object.

payment_cancelled view:
- Called when customer hits "Cancel" on the Stripe hosted page.
- Cancels the PENDING order.
- Redirects back to cart with a warning message.
"""

# apps/payments/views.py
"""
Stripe webhook handler and payment-related views.

Webhook responsibilities (checkout.session.completed):
1. Guard against duplicate processing.
2. Mark order PAID + set is_paid = True.
3. Deduct stock for each order item (only here, never in CheckoutService).
4. Clear the user's cart.
5. Record the Payment object.
6. Fire async confirmation email.

Webhook responsibilities (checkout.session.async_payment_failed):
1. Mark order CANCELLED (only if not already PAID).
2. Record the failed Payment object.

payment_cancelled view:
- Called when customer hits "Cancel" on the Stripe hosted page.
- Cancels the PENDING order.
- Redirects back to cart with a warning message.
"""

import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from apps.core.tasks import send_order_confirmation_email
from apps.orders.models import Order
from apps.products.models import ProductVariant

from .models import Payment, Refund

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─────────────────────────────────────────────────────────────────────────────
# STRIPE WEBHOOK
# ─────────────────────────────────────────────────────────────────────────────

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook endpoint.

    Must be registered in the Stripe dashboard pointing to:
        /payments/webhook/stripe/

    Expected events:
        checkout.session.completed
        checkout.session.async_payment_failed
    """

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

    except ValueError:
        logger.warning("Stripe webhook: invalid payload")
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:
        logger.warning("Stripe webhook: invalid signature")
        return HttpResponse(status=400)

    event_type = event["type"]

    # ─────────────────────────────────────────────────────────
    # PAYMENT SUCCESS
    # ─────────────────────────────────────────────────────────
    if event_type == "checkout.session.completed":
        _handle_payment_success(event["data"]["object"])

    # ─────────────────────────────────────────────────────────
    # PAYMENT FAILED (async instruments — SEPA, OXXO, etc.)
    # ─────────────────────────────────────────────────────────
    elif event_type == "checkout.session.async_payment_failed":
        _handle_payment_failed(event["data"]["object"])

    else:
        logger.info(f"Stripe webhook: unhandled event type '{event_type}'")

    # Always acknowledge receipt to Stripe
    return HttpResponse(status=200)


def _handle_payment_success(session: dict) -> None:
    """
    Process a confirmed Stripe payment.

    Steps:
    1. Validate payment_status == "paid".
    2. Locate the order via metadata.
    3. Guard against duplicate processing.
    4. Deduct stock (with per-variant locking).
    5. Mark order PAID + is_paid = True.
    6. Clear user cart.
    7. Persist Payment record.
    8. Send confirmation email (async, best-effort).
    """

    # Only process fully paid sessions
    if session.get("payment_status") != "paid":
        logger.warning(
            "Stripe webhook: checkout.session.completed received "
            "but payment_status != 'paid'. Skipping."
        )
        return

    metadata = session.get("metadata", {})
    order_id = metadata.get("order_id")

    if not order_id:
        logger.warning(
            "Stripe webhook: checkout.session.completed missing "
            "order_id in metadata. Skipping."
        )
        return

    order_for_email = None

    try:
        with transaction.atomic():

            # Lock order row to prevent race conditions
            order = Order.objects.select_for_update().get(id=order_id)

            # ── Idempotency guard ──────────────────────────────
            if order.status == Order.Status.PAID:
                logger.info(
                    f"Stripe webhook: order {order_id} already PAID. "
                    "Duplicate event ignored."
                )
                return

            # ── Deduct stock ───────────────────────────────────
            # This is the ONLY place stock is deducted for Stripe orders.
            # CheckoutService only validates; deduction is deferred until here.
            for item in order.items.select_related("product_variant"):

                if not item.product_variant_id:
                    logger.warning(
                        f"Stripe webhook: order item {item.id} has no "
                        "linked variant — skipping stock deduction."
                    )
                    continue

                # Lock variant row
                variant = (
                    ProductVariant.objects
                    .select_for_update()
                    .get(id=item.product_variant_id)
                )

                if variant.stock < item.quantity:
                    # Stock ran out between checkout and payment.
                    # Log the anomaly but do NOT block the payment —
                    # the customer already paid; fulfillment team must handle it.
                    logger.error(
                        f"Stripe webhook: insufficient stock for variant "
                        f"{variant.id} on order {order_id}. "
                        f"Available: {variant.stock}, Required: {item.quantity}. "
                        "Marking order PAID but flagging for manual review."
                    )
                    # Allow negative stock here — operations team must review.
                    # Alternatively: clip to 0 with variant.stock = 0
                else:
                    ProductVariant.objects.filter(
                        id=variant.id
                    ).update(
                        stock=F("stock") - item.quantity
                    )

            # ── Mark order paid ────────────────────────────────
            payment_intent = session.get("payment_intent")
            session_id = session.get("id")

            order.status = Order.Status.PAID
            order.is_paid = True

            if payment_intent:
                order.payment_reference = payment_intent

            if session_id:
                order.stripe_session_id = session_id

            order.save(
                update_fields=[
                    "status",
                    "is_paid",
                    "payment_reference",
                    "stripe_session_id",
                ]
            )

            # ── Clear user cart ────────────────────────────────
            # Safe import here to avoid circular at module level
            from apps.cart.models import Cart

            cart = Cart.objects.filter(user=order.user).first()
            if cart:
                cart.items.all().delete()
                logger.info(
                    f"Stripe webhook: cart cleared for user {order.user_id} "
                    f"after payment for order {order_id}."
                )

            # ── Record payment ─────────────────────────────────
            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "gateway": "stripe",
                    "payment_id": payment_intent,
                    "status": "success",
                    "amount": order.total_amount,
                    "currency": settings.STRIPE_CURRENCY,
                },
            )

            logger.info(
                f"Stripe webhook: order {order_id} marked PAID successfully."
            )

            # Keep a reference for the post-commit email send below.
            order_for_email = order

    except Order.DoesNotExist:
        logger.error(
            f"Stripe webhook: order {order_id} not found in database."
        )
        return

    # ── Send confirmation email (non-blocking, best-effort) ────────────
    # IMPORTANT: this runs AFTER the atomic block has committed.
    # If Celery/Redis is unavailable, this must NEVER roll back or
    # otherwise undo the PAID status / stock deduction / cart clear
    # that was already committed above.
    if order_for_email is not None:
        try:
            send_order_confirmation_email.delay(order_for_email.id)
        except Exception as email_error:
            logger.error(
                f"Stripe webhook: failed to queue confirmation email "
                f"for order {order_for_email.id}: {email_error}"
            )


def _handle_payment_failed(session: dict) -> None:
    """
    Handle async payment failure (SEPA, OXXO, bank redirects, etc.).

    Cancels the order if it has not already been paid.
    Stock was never deducted for Stripe orders so no restoration needed.
    """

    metadata = session.get("metadata", {})
    order_id = metadata.get("order_id")

    if not order_id:
        return

    try:
        with transaction.atomic():

            order = Order.objects.select_for_update().get(id=order_id)

            # Never downgrade a paid order
            if order.status == Order.Status.PAID:
                return

            session_id = session.get("id")
            payment_intent = session.get("payment_intent")

            order.status = Order.Status.CANCELLED

            if session_id:
                order.stripe_session_id = session_id

            order.save(
                update_fields=[
                    "status",
                    "stripe_session_id",
                ]
            )

            Payment.objects.update_or_create(
                order=order,
                defaults={
                    "gateway": "stripe",
                    "payment_id": payment_intent,
                    "status": "failed",
                    "amount": order.total_amount,
                    "currency": settings.STRIPE_CURRENCY,
                },
            )

            logger.info(
                f"Stripe webhook: order {order_id} marked CANCELLED "
                "(async payment failed)."
            )

    except Order.DoesNotExist:
        logger.error(
            f"Stripe webhook (failed): order {order_id} not found."
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAYMENT CANCELLED VIEW
# Called when the customer clicks "Cancel" / "Back" on Stripe's hosted page.
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def payment_cancelled(request):
    """
    Handle Stripe payment cancellation.

    Stripe redirects here when the customer exits the hosted checkout page
    without completing payment.

    Actions:
    - Cancel the PENDING order (if found and owned by the current user).
    - Cart is NOT cleared — customer should be able to try again.
    - Redirect to cart with a warning message.
    """

    order_id = request.GET.get("order_id")

    if order_id:
        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user,
            )

            # Only cancel orders that haven't been paid yet
            if order.status == Order.Status.PENDING:
                order.status = Order.Status.CANCELLED
                order.save(update_fields=["status"])

                logger.info(
                    f"Payment cancelled: order {order_id} cancelled "
                    f"by user {request.user.id}."
                )

        except Order.DoesNotExist:
            logger.warning(
                f"Payment cancelled: order {order_id} not found "
                f"for user {request.user.id}."
            )

    messages.warning(
        request,
        "Your payment was cancelled. "
        "Your cart is still saved — you can try again whenever you're ready."
    )

    return redirect("cart_detail")


# ─────────────────────────────────────────────────────────────────────────────
# REFUND REQUEST
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def request_refund(request, order_id):
    """
    Allow authenticated users to request a refund for a paid order.
    """

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user,
    )

    if request.method == "POST":

        reason = request.POST.get("reason", "").strip()

        if reason:
            Refund.objects.create(
                order=order,
                reason=reason,
                amount=order.total_amount,
            )
            messages.success(request, "Refund request submitted successfully.")
        else:
            messages.error(request, "Please provide a reason for the refund.")

    return redirect("order_detail", order_number=order.order_number)