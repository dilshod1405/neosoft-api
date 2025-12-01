from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import PlatformBalance
from .serializers import PlatformBalanceSerializer



class PlatformBalanceAPIView(generics.RetrieveAPIView):
    serializer_class = PlatformBalanceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        return PlatformBalance.objects.get(id=1)
    
