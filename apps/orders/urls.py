from django.urls import path
from .views import (
    order_success,
    user_orders,
    order_detail_view,
    cancel_order,
    download_invoice,
    orders_home_view,
    checkout_page,
    payment_cancelled,
)

urlpatterns = [
    path("", orders_home_view, name="orders_home"),
    path("checkout/", checkout_page, name="checkout_page"),
    path("checkout/stripe/", checkout_page, name="checkout"),
    path("success/", order_success, name="order_success"),
    path("payment-cancelled/", payment_cancelled, name="payment_cancelled"),
    path("my-orders/", user_orders, name="user_orders"),
    path("my-orders/<str:order_number>/", order_detail_view, name="order_detail"),
    path("cancel/<str:order_number>/", cancel_order, name="cancel_order"),
    path("invoice/<int:order_id>/", download_invoice, name="invoice"),
]