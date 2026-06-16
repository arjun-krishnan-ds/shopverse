from django.urls import path
from .views import (
    product_list_view,
    product_detail_view,
    search_products_view,
    search_api_view,
    quickview_product_api,
    products_api_view
)

urlpatterns = [
    path("", product_list_view, name="product_list"),
    path("category/<slug:category_slug>/", product_list_view, name="category_products"),

    # API routes MUST come before the slug catch-all
    path("api/", products_api_view, name="products_api"),
    path("api/search/", search_api_view, name="search_api"),
    path("search/", search_products_view, name="product_search"),
    path("quickview/<int:product_id>/", quickview_product_api, name="quickview_api"),

    # Slug catch-all MUST be last
    path("<slug:slug>/", product_detail_view, name="product_detail"),
]