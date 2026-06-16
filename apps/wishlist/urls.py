from django.urls import path

from .views import add_to_wishlist, remove_from_wishlist, wishlist_list,toggle_wishlist

urlpatterns = [
    path("", wishlist_list, name="wishlist_list"),
    path("add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path("remove/<int:product_id>/", remove_from_wishlist, name="remove_from_wishlist"),
    path("toggle/<int:product_id>/", toggle_wishlist, name="toggle_wishlist"),
]
