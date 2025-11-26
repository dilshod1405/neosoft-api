from django.contrib.auth.backends import ModelBackend
from authentication.models import CustomUser
from utils.get_client_ip import get_client_ip

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, email=None, phone=None, password=None, **kwargs):
        user = None

        if email:
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                pass

        if not user and phone:
            try:
                user = CustomUser.objects.get(phone=phone)
            except CustomUser.DoesNotExist:
                pass

        if not user:
            return None

        if not user.check_password(password):
            return None

        # Country restriction (O'zbekiston)
        ip = get_client_ip(request)
        try:
            from django.contrib.gis.geoip2 import GeoIP2
            country = GeoIP2().country(ip)["country_code"]
            if country != "UZ":
                return None
        except:
            pass

        return user
