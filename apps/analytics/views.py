from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from .services.sales_service import SalesAnalyticsService


@staff_member_required
def admin_dashboard(request):

    context = {
        "total_revenue": SalesAnalyticsService.total_revenue(),
        "revenue_today": SalesAnalyticsService.revenue_today(),
        "revenue_this_month": SalesAnalyticsService.revenue_this_month(),
        "orders_today": SalesAnalyticsService.orders_today(),
        "average_order_value": SalesAnalyticsService.average_order_value(),
        "top_products": SalesAnalyticsService.top_selling_products(),
        "daily_sales": SalesAnalyticsService.daily_sales(),
    }

    return render(
        request,
        "pages/analytics/dashboard.html",
        context
    )