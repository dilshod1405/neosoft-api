from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.template import Template, Context
from django.conf import settings
import os

from authentication.mentors.models import MentorContract, MentorProfile
from utils.generator_contract_pdf import generate_contract_pdf
from .send_contract_sms_code import send_contract_sms
from .contract_text_uz import CONTRACT_TEXT_UZ
from .contract_text_ru import CONTRACT_TEXT_RU


class GenerateContractView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not user.is_mentor:
            return Response({"error": "Siz mentor emassiz."}, status=403)

        try:
            mentor = user.mentor_profile
        except MentorProfile.DoesNotExist:
            return Response({"success": False, "message": "Mentor profili topilmadi."}, status=400)

        contract, created = MentorContract.objects.get_or_create(mentor=mentor)

        if contract.is_signed:
            short_url = request.build_absolute_uri("/api/mentor/contract/download/")
            return Response({
                "success": True,
                "message": "Shartnoma allaqachon imzolangan.",
                "contract_id": contract.pk,
                "contract_number": contract.document_id,
                "short_url": short_url
            })

        if created or not contract.document_id:
            contract.document_id = f"MN-{contract.pk}"
            contract.save()

        required = {
            "passport_number": mentor.passport_number,
            "passport_issued_by": mentor.passport_issued_by,
            "passport_issue_date": mentor.passport_issue_date,
            "address": mentor.address,
            "card_number": mentor.card_number,
            "phone": user.phone,
            "pinfl": mentor.pinfl,
            "dob": mentor.dob,
        }

        missing = [k for k, v in required.items() if not v]
        if missing:
            return Response({
                "success": False,
                "message": "Mentor profili to‘liq emas",
                "missing_fields": missing
            }, status=400)

        if created or not contract.pdf_file:
            lang = request.data.get("lang", "uz")
            template_text = CONTRACT_TEXT_UZ if lang == "uz" else CONTRACT_TEXT_RU

            rendered_body = Template(template_text).render(Context({
                "contract_number": contract.document_id,
                "contract_date": timezone.now().strftime("%d.%m.%Y"),
                "mentor_fio": f"{user.first_name} {user.last_name}",
                "mentor_passport": mentor.passport_number,
                "passport_issued_by": mentor.passport_issued_by,
                "passport_issue_date": mentor.passport_issue_date.strftime("%d.%m.%Y") if mentor.passport_issue_date else "",
                "mentor_address": mentor.address,
                "mentor_phone": user.phone,
                "mentor_card": mentor.card_number,
                "mentor_pinfl": mentor.pinfl or "",
                "mentor_dob": mentor.dob.strftime("%d.%m.%Y") if mentor.dob else "",
            }))


            stamp_path = os.path.join(settings.STATIC_ROOT, "images", "stamp_blue.png")
            if not os.path.exists(stamp_path):
                stamp_path = os.path.join(settings.BASE_DIR, "static", "images", "stamp_blue.png")

            pdf_path = generate_contract_pdf({
                "contract_body": rendered_body,
                "stamp_url": f"file://{os.path.abspath(stamp_path)}",
            })

            private_root = settings.PRIVATE_CONTRACT_ROOT
            os.makedirs(private_root, exist_ok=True)

            final_path = os.path.join(private_root, os.path.basename(pdf_path))
            os.rename(pdf_path, final_path)

            contract.pdf_file = os.path.basename(final_path)
            contract.generated_at = timezone.now()
            contract.is_signed = False

        short_url = request.build_absolute_uri("/api/mentor/contract/download/")
        contract.short_url = short_url
        contract.sent_at = timezone.now()
        contract.save()

        send_contract_sms(mentor.id, user.phone)

        return Response({
            "success": True,
            "message": "Contract PDF tayyorlandi va SMS yuborildi.",
            "contract_id": contract.pk,
            "contract_number": contract.document_id,
            "short_url": short_url
        })
