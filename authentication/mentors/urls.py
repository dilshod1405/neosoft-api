from django.urls import path

from authentication.mentors.contract.generate_contract_view import GenerateContractView
from authentication.mentors.contract.verify_contract_view import VerifyContractSMSView
from .views import MentorApplyView, ContractDownloadView

urlpatterns = [
    path("contract/generate/", GenerateContractView.as_view(), name="generate_contract"),
    path("contract/verify-code/", VerifyContractSMSView.as_view(), name="verify_contract_sms"),
    path("contract/download/", ContractDownloadView.as_view(), name="download_contract"),
    
    path("apply/", MentorApplyView.as_view(), name="become-mentor"),
]
