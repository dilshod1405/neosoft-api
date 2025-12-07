# payment/student/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from payment.models import Transaction
from .serializers import StudentTransactionSerializer

class StudentTransactionHistoryView(generics.ListAPIView):
    serializer_class = StudentTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(order__student=self.request.user).order_by("-created_at")
