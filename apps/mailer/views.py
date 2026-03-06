from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.workspace.models import Workspace
from apps.leads.models import Lead
from apps.campaigns.models import Campaign, CampaignLead, CampaignSequenceStep
from apps.ai_engine.services import build_message_variables
from .models import SMTPSetting, EmailLog
from .serializers import (
    SMTPSettingSerializer,
    SMTPSettingCreateUpdateSerializer,
    TestEmailSerializer,
    SendCampaignEmailSerializer,
    EmailLogListSerializer,
    EmailLogDetailSerializer,
)
from .services import send_email_via_smtp, render_email_content

class MailerBaseMixin:
    def get_workspace(self, user):
        try:
            return user.workspace
        except Workspace.DoesNotExist:
            return None


class SMTPSettingAPIView(APIView, MailerBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            smtp_setting = workspace.smtp_setting
        except SMTPSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "SMTP setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": SMTPSettingSerializer(smtp_setting).data,
            },
            status=status.HTTP_200_OK
        )

    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found. Please create workspace first."},
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(workspace, "smtp_setting"):
            return Response(
                {"status": "error", "message": "SMTP setting already exists. Use update instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SMTPSettingCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            smtp_setting = serializer.save(workspace=workspace)
            return Response(
                {
                    "status": "success",
                    "message": "SMTP setting created successfully.",
                    "data": SMTPSettingSerializer(smtp_setting).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def put(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            smtp_setting = workspace.smtp_setting
        except SMTPSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "SMTP setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SMTPSettingCreateUpdateSerializer(smtp_setting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "SMTP setting updated successfully.",
                    "data": SMTPSettingSerializer(smtp_setting).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            smtp_setting = workspace.smtp_setting
        except SMTPSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "SMTP setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SMTPSettingCreateUpdateSerializer(smtp_setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "SMTP setting updated successfully.",
                    "data": SMTPSettingSerializer(smtp_setting).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    

class SendTestEmailAPIView(APIView, MailerBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            smtp_setting = workspace.smtp_setting
        except SMTPSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "SMTP setting not found. Please configure SMTP first."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not smtp_setting.is_active:
            return Response(
                {"status": "error", "message": "SMTP setting is inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TestEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        to_email = serializer.validated_data["to_email"]
        subject = serializer.validated_data.get("subject") or "SMTP Test Email"
        body = serializer.validated_data.get("body") or "Your SMTP configuration is working."

        email_log = EmailLog.objects.create(
            workspace=workspace,
            to_email=to_email,
            subject=subject,
            body=body,
            status="pending",
            created_by=request.user,
        )

        try:
            result = send_email_via_smtp(
                smtp_setting=smtp_setting,
                to_email=to_email,
                subject=subject,
                body=body,
            )
            email_log.status = "sent"
            email_log.provider_message_id = result["provider_message_id"]
            email_log.sent_at = result["sent_at"]
            email_log.save(update_fields=["status", "provider_message_id", "sent_at"])

            return Response(
                {
                    "status": "success",
                    "message": "Test email sent successfully.",
                    "data": EmailLogDetailSerializer(email_log).data,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.save(update_fields=["status", "error_message"])

            return Response(
                {
                    "status": "error",
                    "message": "Failed to send test email.",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class SendCampaignEmailAPIView(APIView, MailerBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            smtp_setting = workspace.smtp_setting
        except SMTPSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "SMTP setting not found. Please configure SMTP first."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not smtp_setting.is_active:
            return Response(
                {"status": "error", "message": "SMTP setting is inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SendCampaignEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign_id = serializer.validated_data["campaign_id"]
        lead_id = serializer.validated_data["lead_id"]
        sequence_step_id = serializer.validated_data.get("sequence_step_id")
        subject = serializer.validated_data.get("subject", "").strip()
        body = serializer.validated_data.get("body", "").strip()

        try:
            campaign = Campaign.objects.get(id=campaign_id, workspace=workspace)
        except Campaign.DoesNotExist:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            lead = Lead.objects.get(id=lead_id, workspace=workspace)
        except Lead.DoesNotExist:
            return Response(
                {"status": "error", "message": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            campaign_lead = CampaignLead.objects.get(campaign=campaign, lead=lead)
        except CampaignLead.DoesNotExist:
            return Response(
                {"status": "error", "message": "Lead is not assigned to this campaign."},
                status=status.HTTP_404_NOT_FOUND
            )

        sequence_step = None
        if sequence_step_id:
            try:
                sequence_step = CampaignSequenceStep.objects.get(
                    id=sequence_step_id,
                    campaign=campaign
                )
            except CampaignSequenceStep.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Sequence step not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            subject = sequence_step.subject or ""
            body = sequence_step.body or ""

        variables = build_message_variables(workspace=workspace, lead=lead, campaign=campaign)
        subject, body = render_email_content(subject, body, variables)

        if not subject or not body:
            return Response(
                {"status": "error", "message": "Final email subject/body cannot be empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email_log = EmailLog.objects.create(
            workspace=workspace,
            campaign=campaign,
            campaign_lead=campaign_lead,
            lead=lead,
            sequence_step=sequence_step,
            to_email=lead.email,
            subject=subject,
            body=body,
            status="pending",
            created_by=request.user,
        )

        try:
            result = send_email_via_smtp(
                smtp_setting=smtp_setting,
                to_email=lead.email,
                subject=subject,
                body=body,
            )

            email_log.status = "sent"
            email_log.provider_message_id = result["provider_message_id"]
            email_log.sent_at = result["sent_at"]
            email_log.save(update_fields=["status", "provider_message_id", "sent_at"])

            campaign_lead.status = "contacted"
            campaign_lead.last_contacted_at = timezone.now()

            if sequence_step and sequence_step.step_type == "initial":
                campaign_lead.next_follow_up_at = timezone.now() + timezone.timedelta(days=campaign.follow_up_gap_days)
            elif sequence_step and sequence_step.step_type == "follow_up":
                campaign_lead.next_follow_up_at = timezone.now() + timezone.timedelta(days=campaign.follow_up_gap_days)
            elif not sequence_step:
                campaign_lead.next_follow_up_at = timezone.now() + timezone.timedelta(days=campaign.follow_up_gap_days)

            campaign_lead.save(update_fields=["status", "last_contacted_at", "next_follow_up_at"])

            return Response(
                {
                    "status": "success",
                    "message": "Campaign email sent successfully.",
                    "data": EmailLogDetailSerializer(email_log).data,
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            email_log.status = "failed"
            email_log.error_message = str(e)
            email_log.save(update_fields=["status", "error_message"])

            return Response(
                {
                    "status": "error",
                    "message": "Failed to send campaign email.",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class EmailLogListAPIView(APIView, MailerBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = EmailLog.objects.filter(workspace=workspace)

        status_filter = request.GET.get("status", "").strip()
        campaign_id = request.GET.get("campaign_id", "").strip()
        lead_id = request.GET.get("lead_id", "").strip()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)

        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)

        queryset = queryset.order_by("-created_at")

        return Response(
            {
                "status": "success",
                "count": queryset.count(),
                "data": EmailLogListSerializer(queryset, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class EmailLogDetailAPIView(APIView, MailerBaseMixin):
    def get(self, request, log_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            email_log = EmailLog.objects.get(id=log_id, workspace=workspace)
        except EmailLog.DoesNotExist:
            return Response(
                {"status": "error", "message": "Email log not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": EmailLogDetailSerializer(email_log).data,
            },
            status=status.HTTP_200_OK
        )