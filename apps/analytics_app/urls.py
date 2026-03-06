from django.urls import path
from .views import (
    DashboardSummaryAPIView,
    RecentActivityAPIView,
    CampaignPerformanceAPIView,
    LeadStatusBreakdownAPIView,
    CampaignLeadStatusBreakdownAPIView,
    EmailStatusBreakdownAPIView,
)

urlpatterns = [
    path("dashboard-summary/", DashboardSummaryAPIView.as_view(), name="dashboard-summary"),
    path("recent-activity/", RecentActivityAPIView.as_view(), name="recent-activity"),
    path("campaign-performance/", CampaignPerformanceAPIView.as_view(), name="campaign-performance"),
    path("lead-status-breakdown/", LeadStatusBreakdownAPIView.as_view(), name="lead-status-breakdown"),
    path("campaign-lead-status-breakdown/", CampaignLeadStatusBreakdownAPIView.as_view(), name="campaign-lead-status-breakdown"),
    path("email-status-breakdown/", EmailStatusBreakdownAPIView.as_view(), name="email-status-breakdown"),
]