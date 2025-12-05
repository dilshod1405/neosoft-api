from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
import os
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from authentication.mentors.models import MentorContract



@staff_member_required
def admin_contract_download(request, pk):
    contract = get_object_or_404(MentorContract, pk=pk)

    if not contract.pdf_file:
        raise Http404("PDF fayl mavjud emas")

    file_path = os.path.join(settings.PRIVATE_CONTRACT_ROOT, contract.pdf_file.name)
    if not os.path.exists(file_path):
        raise Http404("PDF fayl topilmadi")

    filename = f"{contract.mentor.user.get_full_name()}_contract.pdf"
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=filename)