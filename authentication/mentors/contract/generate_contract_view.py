from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.template import Template, Context
from django.templatetags.static import static
from django.conf import settings
import os

from .contract_text_uz import CONTRACT_TEXT_UZ
from .contract_text_ru import CONTRACT_TEXT_RU
from authentication.mentors.models import MentorContract, MentorProfile
from utils.generator_contract_pdf import generate_contract_pdf


class GenerateContractView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.is_mentor:
            return Response({"error": "Siz mentor emassiz."}, status=403)

        try:
            mentor = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response({
                "success": False,
                "message": "Mentor profili topilmadi."
            }, status=400)

        contract, created = MentorContract.objects.get_or_create(mentor=mentor)

        required = {
            "passport_number": mentor.passport_number,
            "passport_issued_by": mentor.passport_issued_by,
            "passport_issue_date": mentor.passport_issue_date,
            "address": mentor.address,
            "card_number": mentor.card_number,
            "phone": user.phone,
        }
        missing = [k for k, v in required.items() if not v]
        if missing:
            return Response({
                "success": False,
                "message": "Mentor profili to‘liq emas",
                "missing_fields": missing
            }, status=400)

        lang = request.data.get("lang", "uz")
        template_text = CONTRACT_TEXT_UZ if lang == "uz" else CONTRACT_TEXT_RU

        rendered_body = Template(template_text).render(Context({
            "contract_number": f"MN-{contract.pk}",
            "contract_date": timezone.now().strftime("%d.%m.%Y"),
            "mentor_fio": user.full_name,
            "mentor_passport": mentor.passport_number,
            "passport_issued_by": mentor.passport_issued_by,
            "passport_issue_date": mentor.passport_issue_date,
            "mentor_address": mentor.address,
            "mentor_phone": user.phone,
            "mentor_card": mentor.card_number,
        }))


        stamp_path = os.path.join(settings.STATIC_ROOT, "images", "stamp_blue.png")

        if not os.path.exists(stamp_path):
            stamp_path = os.path.join(settings.BASE_DIR, "static", "images", "stamp_blue.png")

        stamp_url = f"file://{os.path.abspath(stamp_path)}"

        pdf_path = generate_contract_pdf({
            "contract_body": rendered_body,
            "stamp_url": stamp_url,
        })

        contract.pdf_file.name = "contracts/" + os.path.basename(pdf_path)
        contract.generated_at = timezone.now()
        contract.save()

        return Response({
            "success": True,
            "message": "Contract PDF generated successfully",
            "pdf_url": request.build_absolute_uri("/media/" + contract.pdf_file.name),
            "contract_id": contract.pk
        })