from celery import shared_task
from apps.orders.models import Order
from apps.core.services.email_service import EmailService


@shared_task
def send_order_confirmation_email(order_id):

    try:
        order = Order.objects.get(id=order_id)
        EmailService.send_order_confirmation(order)
    except Order.DoesNotExist:
        pass