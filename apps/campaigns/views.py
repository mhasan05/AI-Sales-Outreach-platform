from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.workspace.models import Workspace
from apps.leads.models import Lead
from .models import Campaign, CampaignLead, CampaignSequenceStep
from .serializers import (
    CampaignListSerializer,
    CampaignDetailSerializer,
    CampaignCreateUpdateSerializer,
    CampaignLeadAssignSerializer,
    CampaignLeadStatusUpdateSerializer,
    CampaignSequenceStepSerializer,
    CampaignSequenceStepCreateUpdateSerializer,
)


class CampaignBaseMixin:
    def get_workspace(self, user):
        try:
            return user.workspace
        except Workspace.DoesNotExist:
            return None

    def get_campaign(self, workspace, campaign_id):
        try:
            return Campaign.objects.get(workspace=workspace, id=campaign_id)
        except Campaign.DoesNotExist:
            return None
        
class CampaignCreateAPIView(APIView, CampaignBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found. Please create workspace first."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                campaign = serializer.save(workspace=workspace)
                return Response(
                    {
                        "status": "success",
                        "message": "Campaign created successfully.",
                        "data": CampaignDetailSerializer(campaign).data,
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Campaign name already exists in your workspace."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignListAPIView(APIView, CampaignBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = Campaign.objects.filter(workspace=workspace)

        status_filter = request.GET.get("status", "").strip()
        search = request.GET.get("search", "").strip()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if search:
            queryset = queryset.filter(name__icontains=search)

        queryset = queryset.order_by("-created_at")

        return Response(
            {
                "status": "success",
                "count": queryset.count(),
                "data": CampaignListSerializer(queryset, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class CampaignDetailAPIView(APIView, CampaignBaseMixin):
    def get(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": CampaignDetailSerializer(campaign).data,
            },
            status=status.HTTP_200_OK
        )


class CampaignUpdateAPIView(APIView, CampaignBaseMixin):
    def put(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignCreateUpdateSerializer(campaign, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Campaign updated successfully.",
                        "data": CampaignDetailSerializer(campaign).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Campaign name already exists in your workspace."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignCreateUpdateSerializer(campaign, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Campaign updated successfully.",
                        "data": CampaignDetailSerializer(campaign).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "Campaign name already exists in your workspace."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignDeleteAPIView(APIView, CampaignBaseMixin):
    def delete(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign.delete()
        return Response(
            {
                "status": "success",
                "message": "Campaign deleted successfully.",
            },
            status=status.HTTP_200_OK
        )


class CampaignLeadAssignAPIView(APIView, CampaignBaseMixin):
    def post(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignLeadAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        lead_ids = serializer.validated_data["lead_ids"]
        leads = Lead.objects.filter(workspace=workspace, id__in=lead_ids)

        found_ids = set(leads.values_list("id", flat=True))
        requested_ids = set(lead_ids)
        missing_ids = list(requested_ids - found_ids)

        created_count = 0
        skipped_count = 0

        for lead in leads:
            obj, created = CampaignLead.objects.get_or_create(
                campaign=campaign,
                lead=lead,
                defaults={"status": "pending"}
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        return Response(
            {
                "status": "success",
                "message": "Lead assignment completed.",
                "created_count": created_count,
                "skipped_count": skipped_count,
                "missing_ids": missing_ids,
            },
            status=status.HTTP_200_OK
        )


class CampaignLeadListAPIView(APIView, CampaignBaseMixin):
    def get(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = campaign.campaign_leads.select_related("lead").prefetch_related("lead__tags")

        status_filter = request.GET.get("status", "").strip()
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return Response(
            {
                "status": "success",
                "count": queryset.count(),
                "data": [
                    {
                        "id": item.id,
                        "lead_id": item.lead.id,
                        "full_name": item.lead.full_name,
                        "email": item.lead.email,
                        "company_name": item.lead.company_name,
                        "campaign_status": item.status,
                        "last_contacted_at": item.last_contacted_at,
                        "next_follow_up_at": item.next_follow_up_at,
                        "notes": item.notes,
                    }
                    for item in queryset
                ],
            },
            status=status.HTTP_200_OK
        )


class CampaignLeadStatusUpdateAPIView(APIView, CampaignBaseMixin):
    def patch(self, request, campaign_id, campaign_lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            campaign_lead = CampaignLead.objects.get(id=campaign_lead_id, campaign=campaign)
        except CampaignLead.DoesNotExist:
            return Response(
                {"status": "error", "message": "Campaign lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignLeadStatusUpdateSerializer(campaign_lead, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "Campaign lead updated successfully.",
                    "data": CampaignLeadStatusUpdateSerializer(campaign_lead).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignLeadRemoveAPIView(APIView, CampaignBaseMixin):
    def delete(self, request, campaign_id, campaign_lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            campaign_lead = CampaignLead.objects.get(id=campaign_lead_id, campaign=campaign)
        except CampaignLead.DoesNotExist:
            return Response(
                {"status": "error", "message": "Campaign lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign_lead.delete()
        return Response(
            {
                "status": "success",
                "message": "Lead removed from campaign successfully.",
            },
            status=status.HTTP_200_OK
        )


class CampaignSequenceStepCreateAPIView(APIView, CampaignBaseMixin):
    def post(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignSequenceStepCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                step = serializer.save(campaign=campaign)
                return Response(
                    {
                        "status": "success",
                        "message": "Sequence step created successfully.",
                        "data": CampaignSequenceStepSerializer(step).data,
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "This step number already exists in the campaign."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignSequenceStepListAPIView(APIView, CampaignBaseMixin):
    def get(self, request, campaign_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        steps = campaign.sequence_steps.all().order_by("step_number")
        return Response(
            {
                "status": "success",
                "count": steps.count(),
                "data": CampaignSequenceStepSerializer(steps, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class CampaignSequenceStepUpdateAPIView(APIView, CampaignBaseMixin):
    def put(self, request, campaign_id, step_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            step = CampaignSequenceStep.objects.get(id=step_id, campaign=campaign)
        except CampaignSequenceStep.DoesNotExist:
            return Response(
                {"status": "error", "message": "Sequence step not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignSequenceStepCreateUpdateSerializer(step, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Sequence step updated successfully.",
                        "data": CampaignSequenceStepSerializer(step).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "This step number already exists in the campaign."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, campaign_id, step_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            step = CampaignSequenceStep.objects.get(id=step_id, campaign=campaign)
        except CampaignSequenceStep.DoesNotExist:
            return Response(
                {"status": "error", "message": "Sequence step not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CampaignSequenceStepCreateUpdateSerializer(step, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Sequence step updated successfully.",
                        "data": CampaignSequenceStepSerializer(step).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {"status": "error", "message": "This step number already exists in the campaign."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class CampaignSequenceStepDeleteAPIView(APIView, CampaignBaseMixin):
    def delete(self, request, campaign_id, step_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        campaign = self.get_campaign(workspace, campaign_id)
        if not campaign:
            return Response(
                {"status": "error", "message": "Campaign not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            step = CampaignSequenceStep.objects.get(id=step_id, campaign=campaign)
        except CampaignSequenceStep.DoesNotExist:
            return Response(
                {"status": "error", "message": "Sequence step not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        step.delete()
        return Response(
            {
                "status": "success",
                "message": "Sequence step deleted successfully.",
            },
            status=status.HTTP_200_OK
        )