from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import PlatformBalance, PlatformBalanceHistory
from .serializers import PlatformBalanceDetailSerializer



class PlatformBalanceDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PlatformBalanceDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_object(self):
        balance = PlatformBalance.objects.get(id=1)
        history = PlatformBalanceHistory.objects.all().order_by("-created_at")

        return {
            "balance": balance,
            "history": history
        }

    
