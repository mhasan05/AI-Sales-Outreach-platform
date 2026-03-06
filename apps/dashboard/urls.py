from django.urls import path
from .views import (
    login_page,
    register_page,
    dashboard_home,
    workspace_page,
    leads_page,
    campaigns_page,
    ai_messages_page,
    email_logs_page,
)

urlpatterns = [
    path("login/", login_page, name="dashboard-login"),
    path("register/", register_page, name="dashboard-register"),
    path("", dashboard_home, name="dashboard-home"),
    path("workspace/", workspace_page, name="dashboard-workspace"),
    path("leads/", leads_page, name="dashboard-leads"),
    path("campaigns/", campaigns_page, name="dashboard-campaigns"),
    path("ai-messages/", ai_messages_page, name="dashboard-ai-messages"),
    path("email-logs/", email_logs_page, name="dashboard-email-logs"),
]