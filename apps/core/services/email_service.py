# apps/core/services/email_service.py

from django.core.mail import send_mail
from django.conf import settings


class EmailService:

    @staticmethod
    def send_order_confirmation(order):

        subject = f"Order Confirmed - {order.order_number}"

        message = f"""
Hello,

Your order {order.order_number} has been successfully placed.

Total: ₹{order.total_amount}

Thank you for shopping with us.
"""

        recipient = [order.user.email] if order.user and order.user.email else []

        if recipient:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                recipient,
                fail_silently=True,
            )