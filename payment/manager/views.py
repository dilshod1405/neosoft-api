from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.conf import settings
from payment.mentors.models import WithdrawRequest
from payment.mentors.serializers import WithdrawRequestSerializer
from payment.multicard.payout import mentor_create_payout


class WithdrawRequestListView(generics.ListAPIView):
    queryset = WithdrawRequest.objects.all().order_by('-created_at')
    serializer_class = WithdrawRequestSerializer
    permission_classes = [IsAdminUser]


class ApproveWithdrawRequestView(generics.GenericAPIView):
    queryset = WithdrawRequest.objects.all()
    serializer_class = WithdrawRequestSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        withdraw = self.get_object()
        mentor_profile = withdraw.mentor.mentor_profile

        if withdraw.status != "PENDING":
            return Response({"error": "Already processed"}, status=status.HTTP_400_BAD_REQUEST)

        res = mentor_create_payout(mentor_profile, withdraw.amount, withdraw.id)

        if not res.get("success"):
            return Response({"success": False, "multicard_error": res.get("error")}, status=status.HTTP_400_BAD_REQUEST)

        data = res.get("data", res.get("confirmed", {}).get("data", {}))

        withdraw.status = "APPROVED"
        withdraw.multicard_transaction_id = data.get("id")
        withdraw.multicard_uuid = data.get("uuid")
        withdraw.save()

        return Response({
            "success": True,
            "withdraw_id": withdraw.id,
            "multicard_id": data.get("id"),
            "status": data.get("status")
        })
