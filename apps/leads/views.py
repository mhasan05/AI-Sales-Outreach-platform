from django.db import IntegrityError
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.workspace.models import Workspace
from .models import Lead
from .serializers import (
    LeadListSerializer,
    LeadDetailSerializer,
    LeadCreateUpdateSerializer,
    LeadCSVImportSerializer,
)


class LeadBaseMixin:
    def get_workspace(self, user):
        try:
            return user.workspace
        except Workspace.DoesNotExist:
            return None


class LeadCreateAPIView(APIView, LeadBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found. Please create workspace first."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadCreateUpdateSerializer(
            data=request.data,
            context={"workspace": workspace}
        )

        if serializer.is_valid():
            try:
                lead = serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Lead created successfully.",
                        "data": LeadDetailSerializer(lead).data,
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {
                        "status": "error",
                        "message": "A lead with this email already exists in your workspace."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {
                "status": "error",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class LeadListAPIView(APIView, LeadBaseMixin):
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

        queryset = Lead.objects.filter(workspace=workspace).prefetch_related("tags")

        search = request.GET.get("search", "").strip()
        status_filter = request.GET.get("status", "").strip()
        company_name = request.GET.get("company_name", "").strip()

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(company_name__icontains=search)
            )

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if company_name:
            queryset = queryset.filter(company_name__icontains=company_name)

        queryset = queryset.order_by("-created_at")
        serializer = LeadListSerializer(queryset, many=True)

        return Response(
            {
                "status": "success",
                "count": queryset.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK
        )


class LeadDetailAPIView(APIView, LeadBaseMixin):
    def get_object(self, workspace, lead_id):
        try:
            return Lead.objects.prefetch_related("tags").get(id=lead_id, workspace=workspace)
        except Lead.DoesNotExist:
            return None

    def get(self, request, lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        lead = self.get_object(workspace, lead_id)
        if not lead:
            return Response(
                {"status": "error", "message": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": LeadDetailSerializer(lead).data,
            },
            status=status.HTTP_200_OK
        )


class LeadUpdateAPIView(APIView, LeadBaseMixin):
    def get_object(self, workspace, lead_id):
        try:
            return Lead.objects.get(id=lead_id, workspace=workspace)
        except Lead.DoesNotExist:
            return None

    def put(self, request, lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        lead = self.get_object(workspace, lead_id)
        if not lead:
            return Response(
                {"status": "error", "message": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadCreateUpdateSerializer(
            lead,
            data=request.data,
            context={"workspace": workspace}
        )
        if serializer.is_valid():
            try:
                lead = serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Lead updated successfully.",
                        "data": LeadDetailSerializer(lead).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {
                        "status": "error",
                        "message": "A lead with this email already exists in your workspace."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        lead = self.get_object(workspace, lead_id)
        if not lead:
            return Response(
                {"status": "error", "message": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadCreateUpdateSerializer(
            lead,
            data=request.data,
            partial=True,
            context={"workspace": workspace}
        )
        if serializer.is_valid():
            try:
                lead = serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "Lead updated successfully.",
                        "data": LeadDetailSerializer(lead).data,
                    },
                    status=status.HTTP_200_OK
                )
            except IntegrityError:
                return Response(
                    {
                        "status": "error",
                        "message": "A lead with this email already exists in your workspace."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


class LeadDeleteAPIView(APIView, LeadBaseMixin):
    def delete(self, request, lead_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            lead = Lead.objects.get(id=lead_id, workspace=workspace)
        except Lead.DoesNotExist:
            return Response(
                {"status": "error", "message": "Lead not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        lead.delete()
        return Response(
            {
                "status": "success",
                "message": "Lead deleted successfully.",
            },
            status=status.HTTP_200_OK
        )


class LeadCSVImportAPIView(APIView, LeadBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {
                    "status": "error",
                    "message": "Workspace not found. Please create workspace first."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LeadCSVImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        rows = serializer.parse_csv()

        created_count = 0
        skipped_count = 0
        errors = []

        for index, row in enumerate(rows, start=2):
            email = (row.get("email") or "").strip().lower()
            first_name = (row.get("first_name") or "").strip()
            company_name = (row.get("company_name") or "").strip()

            if not email or not first_name or not company_name:
                errors.append(
                    {
                        "row": index,
                        "message": "first_name, email and company_name are required."
                    }
                )
                skipped_count += 1
                continue

            if Lead.objects.filter(workspace=workspace, email=email).exists():
                skipped_count += 1
                continue

            status_value = (row.get("status") or "new").strip()
            valid_statuses = [choice[0] for choice in Lead.STATUS_CHOICES]
            if status_value not in valid_statuses:
                status_value = "new"

            lead = Lead.objects.create(
                workspace=workspace,
                first_name=first_name,
                last_name=(row.get("last_name") or "").strip() or None,
                email=email,
                phone=(row.get("phone") or "").strip() or None,
                company_name=company_name,
                company_website=(row.get("company_website") or "").strip() or None,
                industry=(row.get("industry") or "").strip() or None,
                job_title=(row.get("job_title") or "").strip() or None,
                linkedin_url=(row.get("linkedin_url") or "").strip() or None,
                city=(row.get("city") or "").strip() or None,
                country=(row.get("country") or "").strip() or None,
                status=status_value,
                notes=(row.get("notes") or "").strip() or None,
            )

            raw_tags = (row.get("tags") or "").strip()
            if raw_tags:
                tag_list = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
                tags = []
                for tag_name in tag_list:
                    tag, _ = workspace.lead_tags.get_or_create(name=tag_name)
                    tags.append(tag)
                lead.tags.set(tags)

            created_count += 1

        return Response(
            {
                "status": "success",
                "message": "CSV import completed.",
                "created_count": created_count,
                "skipped_count": skipped_count,
                "errors": errors,
            },
            status=status.HTTP_200_OK
        )