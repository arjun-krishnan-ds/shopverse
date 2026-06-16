from django.urls import path
from .views import delivery_fee


urlpatterns = [
    path("fee/", delivery_fee, name="delivery_fee"),
]