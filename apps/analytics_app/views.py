from itertools import chain

from django.db.models import Count, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.workspace.models import Workspace
from apps.leads.models import Lead
from apps.campaigns.models import Campaign, CampaignLead
from apps.ai_engine.models import AIGeneratedMessage
from apps.mailer.models import EmailLog
from .serializers import (
    DashboardSummarySerializer,
    RecentActivitySerializer,
    CampaignPerformanceSerializer,
    LeadStatusBreakdownSerializer,
    EmailStatusBreakdownSerializer,
)

class AnalyticsBaseMixin:
    def get_workspace(self, user):
        try:
            return user.workspace
        except Workspace.DoesNotExist:
            return None


class DashboardSummaryAPIView(APIView, AnalyticsBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        total_leads = Lead.objects.filter(workspace=workspace).count()
        total_campaigns = Campaign.objects.filter(workspace=workspace).count()
        total_ai_messages = AIGeneratedMessage.objects.filter(workspace=workspace).count()

        total_sent_emails = EmailLog.objects.filter(
            workspace=workspace,
            status="sent"
        ).count()

        total_failed_emails = EmailLog.objects.filter(
            workspace=workspace,
            status="failed"
        ).count()

        total_pending_emails = EmailLog.objects.filter(
            workspace=workspace,
            status="pending"
        ).count()

        interested_leads = CampaignLead.objects.filter(
            campaign__workspace=workspace,
            status="interested"
        ).count()

        meetings_booked = CampaignLead.objects.filter(
            campaign__workspace=workspace,
            status="meeting_booked"
        ).count()

        active_campaigns = Campaign.objects.filter(
            workspace=workspace,
            status="active"
        ).count()

        paused_campaigns = Campaign.objects.filter(
            workspace=workspace,
            status="paused"
        ).count()

        completed_campaigns = Campaign.objects.filter(
            workspace=workspace,
            status="completed"
        ).count()

        data = {
            "total_leads": total_leads,
            "total_campaigns": total_campaigns,
            "total_ai_messages": total_ai_messages,
            "total_sent_emails": total_sent_emails,
            "total_failed_emails": total_failed_emails,
            "total_pending_emails": total_pending_emails,
            "interested_leads": interested_leads,
            "meetings_booked": meetings_booked,
            "active_campaigns": active_campaigns,
            "paused_campaigns": paused_campaigns,
            "completed_campaigns": completed_campaigns,
        }

        return Response(
            {
                "status": "success",
                "data": DashboardSummarySerializer(data).data,
            },
            status=status.HTTP_200_OK
        )


class RecentActivityAPIView(APIView, AnalyticsBaseMixin):
    """
    Returns recent activities from:
    - leads
    - campaigns
    - AI generated messages
    - email logs
    """

    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        limit = request.GET.get("limit", 10)

        try:
            limit = int(limit)
        except ValueError:
            limit = 10

        if limit <= 0:
            limit = 10

        leads = Lead.objects.filter(workspace=workspace).order_by("-created_at")[:limit]
        campaigns = Campaign.objects.filter(workspace=workspace).order_by("-created_at")[:limit]
        ai_messages = AIGeneratedMessage.objects.filter(workspace=workspace).order_by("-created_at")[:limit]
        email_logs = EmailLog.objects.filter(workspace=workspace).order_by("-created_at")[:limit]

        activities = []

        for lead in leads:
            activities.append({
                "type": "lead",
                "title": "New lead added",
                "description": f"{lead.full_name} from {lead.company_name}",
                "created_at": lead.created_at,
            })

        for campaign in campaigns:
            activities.append({
                "type": "campaign",
                "title": "Campaign created",
                "description": campaign.name,
                "created_at": campaign.created_at,
            })

        for message in ai_messages:
            lead_email = message.lead.email if message.lead else "N/A"
            activities.append({
                "type": "ai_message",
                "title": "AI message generated",
                "description": f"{message.message_type} for {lead_email}",
                "created_at": message.created_at,
            })

        for email_log in email_logs:
            activities.append({
                "type": "email",
                "title": f"Email {email_log.status}",
                "description": f"{email_log.to_email} | {email_log.subject}",
                "created_at": email_log.created_at,
            })

        activities = sorted(activities, key=lambda x: x["created_at"], reverse=True)[:limit]

        return Response(
            {
                "status": "success",
                "count": len(activities),
                "data": RecentActivitySerializer(activities, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class CampaignPerformanceAPIView(APIView, AnalyticsBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        campaigns = Campaign.objects.filter(workspace=workspace).order_by("-created_at")

        data = []

        for campaign in campaigns:
            campaign_leads = CampaignLead.objects.filter(campaign=campaign)
            email_logs = EmailLog.objects.filter(campaign=campaign)

            data.append({
                "campaign_id": campaign.id,
                "campaign_name": campaign.name,
                "campaign_status": campaign.status,
                "total_assigned_leads": campaign_leads.count(),
                "contacted": campaign_leads.filter(status="contacted").count(),
                "replied": campaign_leads.filter(status="replied").count(),
                "interested": campaign_leads.filter(status="interested").count(),
                "meetings_booked": campaign_leads.filter(status="meeting_booked").count(),
                "completed": campaign_leads.filter(status="completed").count(),
                "sent_emails": email_logs.filter(status="sent").count(),
                "failed_emails": email_logs.filter(status="failed").count(),
            })

        return Response(
            {
                "status": "success",
                "count": len(data),
                "data": CampaignPerformanceSerializer(data, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class LeadStatusBreakdownAPIView(APIView, AnalyticsBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        data = (
            Lead.objects
            .filter(workspace=workspace)
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        return Response(
            {
                "status": "success",
                "data": LeadStatusBreakdownSerializer(data, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class CampaignLeadStatusBreakdownAPIView(APIView, AnalyticsBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        campaign_id = request.GET.get("campaign_id")

        queryset = CampaignLead.objects.filter(campaign__workspace=workspace)

        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)

        data = (
            queryset
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        return Response(
            {
                "status": "success",
                "data": LeadStatusBreakdownSerializer(data, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class EmailStatusBreakdownAPIView(APIView, AnalyticsBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        campaign_id = request.GET.get("campaign_id")
        lead_id = request.GET.get("lead_id")

        queryset = EmailLog.objects.filter(workspace=workspace)

        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)

        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)

        data = (
            queryset
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )

        return Response(
            {
                "status": "success",
                "data": EmailStatusBreakdownSerializer(data, many=True).data,
            },
            status=status.HTTP_200_OK
        )