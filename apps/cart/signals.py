from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from apps.cart.utils import merge_guest_cart_to_user


@receiver(user_logged_in, dispatch_uid="merge_cart_on_login")
def merge_cart_on_login(sender, request, user, **kwargs):
    """
    NOTE: This signal fires AFTER django.contrib.auth.login()
    has already called request.session.cycle_key(), which
    rotates the session id. By this point,
    request.session.session_key is the NEW session id, which
    will never match a guest Cart's session_id (saved under the
    OLD session id before login).

    Because of this, the actual guest-cart merge is performed
    explicitly in apps.accounts.views.login_view and
    register_view, where the OLD session_key is captured
    BEFORE login() is called and passed directly to
    merge_guest_cart_to_user(session_key, user).

    This signal receiver is kept registered (for dispatch_uid
    stability and in case other code relies on the signal
    existing) but intentionally does nothing, since calling
    merge_guest_cart_to_user(request.session.session_key, user)
    here would silently no-op on a stale/rotated session key.
    """

    pass