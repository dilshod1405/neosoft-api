from django.urls import path

from authentication.mentors.contract.generate_contract_view import GenerateContractView
from .views import MentorApplyView

urlpatterns = [
    path("generate-contract/", GenerateContractView.as_view(), name="generate_contract"),
    
    path("apply/", MentorApplyView.as_view()),
]
