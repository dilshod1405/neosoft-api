from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from permissions.user_permissions import IsOwner, IsMentor
from .models import MentorBalanceHistory, MentorBalance, WithdrawRequest

class MentorBalanceDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwner, IsMentor]

    def get(self, request, *args, **kwargs):
        user = request.user

        balance = MentorBalance.objects.filter(mentor=user).first()
        balance_history = MentorBalanceHistory.objects.filter(mentor=user)
        withdraws = WithdrawRequest.objects.filter(mentor=user)

        from .serializers import MentorBalanceSerializer, MentorBalanceHistorySerializer, WithdrawRequestSerializer

        return Response({
            "balance": MentorBalanceSerializer(balance).data if balance else {"balance": 0},
            "balance_history": MentorBalanceHistorySerializer(balance_history, many=True).data,
            "withdraw_requests": WithdrawRequestSerializer(withdraws, many=True).data,
        })