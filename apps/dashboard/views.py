from django.shortcuts import render


def login_page(request):
    return render(request, "dashboard/auth/login.html")


def register_page(request):
    return render(request, "dashboard/auth/register.html")


def dashboard_home(request):
    return render(request, "dashboard/dashboard.html")


def workspace_page(request):
    return render(request, "dashboard/workspace.html")


def leads_page(request):
    return render(request, "dashboard/leads.html")


def campaigns_page(request):
    return render(request, "dashboard/campaigns.html")


def ai_messages_page(request):
    return render(request, "dashboard/ai_messages.html")


def email_logs_page(request):
    return render(request, "dashboard/email_logs.html")