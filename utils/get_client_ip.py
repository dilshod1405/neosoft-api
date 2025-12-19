import ipaddress

def get_client_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        ip = x_forwarded.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    if not ip:
        return None

    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return None
    except (ValueError, TypeError):
        return None

    return str(ip_obj)
