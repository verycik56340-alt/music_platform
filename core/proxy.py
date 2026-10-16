def get_client_ip(request):
    """
    IP клиента за reverse-proxy.

    При BEHIND_PROXY=True используется django-axes (AXES_CLIENT_IP_CALLABLE)
    и django-ratelimit (RATELIMIT_IP_META_KEY, dotted path к вызываемому
    объекту - при отсутствии заголовка вызывается fallback, а не 500).
    """
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
