from django.urls import path
from .views import (
    WorkspaceCreateAPIView,
    WorkspaceDetailAPIView,
    WorkspaceUpdateAPIView,
)

urlpatterns = [
    path("create/", WorkspaceCreateAPIView.as_view(), name="workspace-create"),
    path("detail/", WorkspaceDetailAPIView.as_view(), name="workspace-detail"),
    path("update/", WorkspaceUpdateAPIView.as_view(), name="workspace-update"),
]