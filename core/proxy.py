def get_client_ip(request):
    """
    Client IP behind a reverse-proxy.

    With BEHIND_PROXY=True it is used by django-axes (AXES_CLIENT_IP_CALLABLE)
    and django-ratelimit (RATELIMIT_IP_META_KEY, a dotted path to the callable
    object - when the header is missing the fallback is called instead of a 500).
    """
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
