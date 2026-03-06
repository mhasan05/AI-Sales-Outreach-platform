from django.urls import path
from .views import (
    CampaignCreateAPIView,
    CampaignListAPIView,
    CampaignDetailAPIView,
    CampaignUpdateAPIView,
    CampaignDeleteAPIView,
    CampaignLeadAssignAPIView,
    CampaignLeadListAPIView,
    CampaignLeadStatusUpdateAPIView,
    CampaignLeadRemoveAPIView,
    CampaignSequenceStepCreateAPIView,
    CampaignSequenceStepListAPIView,
    CampaignSequenceStepUpdateAPIView,
    CampaignSequenceStepDeleteAPIView,
)

urlpatterns = [
    path("create/", CampaignCreateAPIView.as_view(), name="campaign-create"),
    path("list/", CampaignListAPIView.as_view(), name="campaign-list"),
    path("detail/<int:campaign_id>/", CampaignDetailAPIView.as_view(), name="campaign-detail"),
    path("update/<int:campaign_id>/", CampaignUpdateAPIView.as_view(), name="campaign-update"),
    path("delete/<int:campaign_id>/", CampaignDeleteAPIView.as_view(), name="campaign-delete"),

    path("<int:campaign_id>/assign-leads/", CampaignLeadAssignAPIView.as_view(), name="campaign-assign-leads"),
    path("<int:campaign_id>/leads/", CampaignLeadListAPIView.as_view(), name="campaign-leads"),
    path("<int:campaign_id>/leads/<int:campaign_lead_id>/update/", CampaignLeadStatusUpdateAPIView.as_view(), name="campaign-lead-update"),
    path("<int:campaign_id>/leads/<int:campaign_lead_id>/delete/", CampaignLeadRemoveAPIView.as_view(), name="campaign-lead-delete"),

    path("<int:campaign_id>/steps/create/", CampaignSequenceStepCreateAPIView.as_view(), name="campaign-step-create"),
    path("<int:campaign_id>/steps/", CampaignSequenceStepListAPIView.as_view(), name="campaign-step-list"),
    path("<int:campaign_id>/steps/<int:step_id>/update/", CampaignSequenceStepUpdateAPIView.as_view(), name="campaign-step-update"),
    path("<int:campaign_id>/steps/<int:step_id>/delete/", CampaignSequenceStepDeleteAPIView.as_view(), name="campaign-step-delete"),
]