from django.urls import path
from authentication.manager.views.contract_download_view import admin_contract_download

urlpatterns = [
    
    path("contract/download/<int:pk>/", admin_contract_download, name="admin-download-contract")


]
