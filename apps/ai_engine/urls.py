from django.urls import path
from .views import (
    AIProviderSettingAPIView,
    GenerateMessageAPIView,
    AIGeneratedMessageListAPIView,
    AIGeneratedMessageDetailAPIView,
)

urlpatterns = [
    path("provider-setting/", AIProviderSettingAPIView.as_view(), name="ai-provider-setting"),
    path("generate/", GenerateMessageAPIView.as_view(), name="ai-generate-message"),
    path("messages/", AIGeneratedMessageListAPIView.as_view(), name="ai-generated-message-list"),
    path("messages/<int:message_id>/", AIGeneratedMessageDetailAPIView.as_view(), name="ai-generated-message-detail"),
]