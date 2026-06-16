from django.urls import path

from .views import (
    register_view,
    login_view,
    logout_view,
    dashboard_view,

    address_list_view,
    add_address_view,
    edit_address_view,
    delete_address_view,
    set_default_address_view,
)

urlpatterns = [

    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("dashboard/", dashboard_view, name="dashboard_home"),

    # addresses
    path("addresses/", address_list_view, name="address_list"),

    path(
        "addresses/add/",
        add_address_view,
        name="add_address"
    ),

    path(
        "addresses/<int:id>/edit/",
        edit_address_view,
        name="edit_address"
    ),

    path(
        "addresses/<int:id>/delete/",
        delete_address_view,
        name="delete_address"
    ),

    path(
        "addresses/<int:id>/default/",
        set_default_address_view,
        name="set_default_address"
    ),
]


