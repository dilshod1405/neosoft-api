from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utils.get_redis import get_redis
from django.utils import timezone
from payment.mentors.models import MentorBalance


class VerifyContractSMSView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        phone = request.user.phone
        code = request.data.get("code")

        if not code:
            return Response({"error": "Kod yuborilmadi"}, status=400)

        redis = get_redis()
        redis_key = f"sms_code:{phone}"

        stored_code = redis.get(redis_key)

        if stored_code is None:
            return Response({
                "success": False,
                "message": "Kod muddati tugagan (yoki yuborilmagan)"
            }, status=400)

        if stored_code != code:
            return Response({
                "success": False,
                "message": "Kod noto‘g‘ri"
            }, status=400)

        redis.delete(redis_key)

        contract = request.user.mentor_profile.contract
        contract.is_signed = True
        contract.signed_at = timezone.now()
        contract.status = 1
        contract.save()

        MentorBalance.objects.get_or_create(mentor=request.user)

        return Response({
            "success": True,
            "message": "Shartnoma tasdiqlandi"
        })
