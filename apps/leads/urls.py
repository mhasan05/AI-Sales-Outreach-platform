from django.urls import path
from .views import (
    LeadCreateAPIView,
    LeadListAPIView,
    LeadDetailAPIView,
    LeadUpdateAPIView,
    LeadDeleteAPIView,
    LeadCSVImportAPIView,
)

urlpatterns = [
    path("create/", LeadCreateAPIView.as_view(), name="lead-create"),
    path("list/", LeadListAPIView.as_view(), name="lead-list"),
    path("detail/<int:lead_id>/", LeadDetailAPIView.as_view(), name="lead-detail"),
    path("update/<int:lead_id>/", LeadUpdateAPIView.as_view(), name="lead-update"),
    path("delete/<int:lead_id>/", LeadDeleteAPIView.as_view(), name="lead-delete"),
    path("import-csv/", LeadCSVImportAPIView.as_view(), name="lead-import-csv"),
]