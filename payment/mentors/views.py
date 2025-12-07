from rest_framework import generics, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from permissions.user_permissions import IsOwner, IsMentor
from .models import MentorBalanceHistory, MentorBalance, WithdrawRequest
from .serializers import MentorWithdrawRequestCreateSerializer
from payment.manager.serializers import WithdrawRequestSerializer
from payment.mentors.serializers import MentorBalanceSerializer, MentorBalanceHistorySerializer



class MentorBalanceDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwner, IsMentor]

    def get(self, request, *args, **kwargs):
        user = request.user

        balance = MentorBalance.objects.filter(mentor=user).first()
        balance_history = MentorBalanceHistory.objects.filter(mentor=user)
        withdraws = WithdrawRequest.objects.filter(mentor=user)

        return Response({
            "balance": MentorBalanceSerializer(balance).data if balance else {"balance": 0},
            "balance_history": MentorBalanceHistorySerializer(balance_history, many=True).data,
            "withdraw_requests": WithdrawRequestSerializer(withdraws, many=True).data,
        })




class MentorWithdrawRequestCreateView(generics.CreateAPIView):
    serializer_class = MentorWithdrawRequestCreateSerializer
    permission_classes = [IsAuthenticated, IsMentor]

    def perform_create(self, serializer):
        mentor = self.request.user
        balance_obj, _ = MentorBalance.objects.get_or_create(mentor=mentor)

        amount = serializer.validated_data["amount"]

        if amount <= 0:
            raise serializers.ValidationError({"amount": "Pul miqdori manfiy bo'lmasligi kerak !"})

        if balance_obj.balance < amount:
            raise serializers.ValidationError({"amount": "Hisobingizda mablag' yetarli emas !"})

        serializer.save(mentor=mentor)
    




class MentorWithdrawHistoryView(generics.ListAPIView):
    serializer_class = WithdrawRequestSerializer
    permission_classes = [IsAuthenticated, IsMentor]

    def get_queryset(self):
        return WithdrawRequest.objects.filter(mentor=self.request.user).order_by("-created_at")
