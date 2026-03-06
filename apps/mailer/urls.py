from django.urls import path
from .views import (
    SMTPSettingAPIView,
    SendTestEmailAPIView,
    SendCampaignEmailAPIView,
    EmailLogListAPIView,
    EmailLogDetailAPIView,
)

urlpatterns = [
    path("smtp-setting/", SMTPSettingAPIView.as_view(), name="smtp-setting"),
    path("send-test-email/", SendTestEmailAPIView.as_view(), name="send-test-email"),
    path("send-campaign-email/", SendCampaignEmailAPIView.as_view(), name="send-campaign-email"),
    path("logs/", EmailLogListAPIView.as_view(), name="email-log-list"),
    path("logs/<int:log_id>/", EmailLogDetailAPIView.as_view(), name="email-log-detail"),
]