from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    # Cart page
    path("", views.cart_detail_view, name="cart_detail"),

    # Cart JSON API
    path("json/", views.cart_json_view, name="cart_json"),

    # Add item
    path("add/<int:variant_id>/", views.add_to_cart_view, name="add_to_cart"),

    # Update quantity
    path("update/", views.update_cart_item_view, name="update_cart"),

    # Remove item
    path("remove/", views.remove_from_cart_view, name="remove_from_cart"),
]