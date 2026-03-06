from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),

    path("dashboard/", include("apps.dashboard.urls")),

    path("api/auth/", include("apps.accounts.urls")),
    path("api/workspace/", include("apps.workspace.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/campaigns/", include("apps.campaigns.urls")),
    path("api/ai/", include("apps.ai_engine.urls")),
    path("api/mailer/", include("apps.mailer.urls")),
    path("api/analytics/", include("apps.analytics_app.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)