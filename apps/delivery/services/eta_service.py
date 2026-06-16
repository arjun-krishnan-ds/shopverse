from datetime import timedelta
from django.utils import timezone


class ETAService:

    @staticmethod
    def estimate(order):

        if order.status == "paid":
            return timezone.now() + timedelta(days=5)

        if order.status == "shipped":
            return timezone.now() + timedelta(days=2)

        if order.status == "out_for_delivery":
            return timezone.now() + timedelta(hours=6)

        return None