from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from apps.orders.models import Order, OrderItem


class SalesAnalyticsService:

    @staticmethod
    def total_revenue():
        return (
            Order.objects
            .filter(status="paid")
            .aggregate(total=Sum("total_amount"))["total"] or 0
        )

    @staticmethod
    def revenue_today():

        today = timezone.now().date()

        return (
            Order.objects
            .filter(status="paid", created_at__date=today)
            .aggregate(total=Sum("total_amount"))["total"] or 0
        )

    @staticmethod
    def orders_today():

        today = timezone.now().date()

        return (
            Order.objects
            .filter(created_at__date=today)
            .count()
        )

    @staticmethod
    def revenue_this_month():

        now = timezone.now()

        return (
            Order.objects
            .filter(
                status="paid",
                created_at__year=now.year,
                created_at__month=now.month
            )
            .aggregate(total=Sum("total_amount"))["total"] or 0
        )

    @staticmethod
    def average_order_value():

        revenue = SalesAnalyticsService.total_revenue()

        orders = (
            Order.objects
            .filter(status="paid")
            .count()
        )

        if orders == 0:
            return 0

        return revenue / orders

    @staticmethod
    def top_selling_products(limit=5):

        return (
            OrderItem.objects
            .values("product_name")
            .annotate(
                total_sold=Sum("quantity")
            )
            .order_by("-total_sold")[:limit]
        )

    @staticmethod
    def daily_sales(days=7):

        today = timezone.now().date()
        start_date = today - timedelta(days=days)

        sales = (
            Order.objects
            .filter(
                status="paid",
                created_at__date__gte=start_date
            )
            .values("created_at__date")
            .annotate(
                revenue=Sum("total_amount"),
                orders=Count("id")
            )
            .order_by("created_at__date")
        )

        return sales