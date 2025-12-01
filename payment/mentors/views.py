from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from payment.models import Transaction
from .serializers import MentorTransactionSerializer

class MentorTransactionsAPIView(generics.ListAPIView):
    serializer_class = MentorTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only Mentor's own transactions
        user = self.request.user
        qs = Transaction.objects.filter(order__course__instructor__user=user)
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status.upper())
            return qs.order_by("-created_at")
        
        if not getattr(user, "is_mentor", False):
            return Transaction.objects.none()

        return Transaction.objects.filter(
            order__course__instructor__user=user
        ).order_by("-created_at")
