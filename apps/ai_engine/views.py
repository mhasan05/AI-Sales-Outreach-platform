from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.workspace.models import Workspace
from apps.leads.models import Lead
from apps.campaigns.models import Campaign, CampaignSequenceStep
from .models import AIProviderSetting, AIGeneratedMessage
from .serializers import (
    AIProviderSettingSerializer,
    AIProviderSettingCreateUpdateSerializer,
    AIGeneratedMessageListSerializer,
    AIGeneratedMessageDetailSerializer,
    GenerateMessageSerializer,
)
from .services import (
    build_message_variables,
    build_prompt,
    call_openai_chat_completion,
    parse_ai_json_content,
)


class AIBaseMixin:
    def get_workspace(self, user):
        try:
            return user.workspace
        except Workspace.DoesNotExist:
            return None


class AIProviderSettingAPIView(APIView, AIBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            provider_setting = workspace.ai_provider_setting
        except AIProviderSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "AI provider setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": AIProviderSettingSerializer(provider_setting).data,
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

        if hasattr(workspace, "ai_provider_setting"):
            return Response(
                {"status": "error", "message": "AI provider setting already exists. Use update instead."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AIProviderSettingCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            provider_setting = serializer.save(workspace=workspace)
            return Response(
                {
                    "status": "success",
                    "message": "AI provider setting created successfully.",
                    "data": AIProviderSettingSerializer(provider_setting).data,
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
            provider_setting = workspace.ai_provider_setting
        except AIProviderSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "AI provider setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AIProviderSettingCreateUpdateSerializer(provider_setting, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "AI provider setting updated successfully.",
                    "data": AIProviderSettingSerializer(provider_setting).data,
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
            provider_setting = workspace.ai_provider_setting
        except AIProviderSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "AI provider setting not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AIProviderSettingCreateUpdateSerializer(provider_setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "message": "AI provider setting updated successfully.",
                    "data": AIProviderSettingSerializer(provider_setting).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    


class GenerateMessageAPIView(APIView, AIBaseMixin):
    def post(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found. Please create workspace first."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            provider_setting = workspace.ai_provider_setting
        except AIProviderSetting.DoesNotExist:
            return Response(
                {"status": "error", "message": "AI provider setting not found. Please configure AI first."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not provider_setting.is_active:
            return Response(
                {"status": "error", "message": "AI provider setting is inactive."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = GenerateMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"status": "error", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        campaign = None
        lead = None
        sequence_step = None

        campaign_id = validated_data.get("campaign_id")
        lead_id = validated_data.get("lead_id")
        sequence_step_id = validated_data.get("sequence_step_id")
        message_type = validated_data.get("message_type")
        custom_instruction = validated_data.get("custom_instruction", "")
        create_sequence_step = validated_data.get("create_sequence_step", False)

        if campaign_id:
            try:
                campaign = Campaign.objects.get(id=campaign_id, workspace=workspace)
            except Campaign.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Campaign not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        if lead_id:
            try:
                lead = Lead.objects.get(id=lead_id, workspace=workspace)
            except Lead.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Lead not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        if sequence_step_id:
            try:
                sequence_step = CampaignSequenceStep.objects.get(
                    id=sequence_step_id,
                    campaign__workspace=workspace
                )
            except CampaignSequenceStep.DoesNotExist:
                return Response(
                    {"status": "error", "message": "Sequence step not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

        variables = build_message_variables(workspace=workspace, lead=lead, campaign=campaign)
        system_prompt, user_prompt = build_prompt(
            message_type=message_type,
            variables=variables,
            custom_instruction=custom_instruction,
        )

        try:
            raw_response, content = call_openai_chat_completion(
                api_key=provider_setting.api_key,
                model_name=provider_setting.model_name or None,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
            parsed = parse_ai_json_content(content)
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": "AI generation failed.",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        generated_message = AIGeneratedMessage.objects.create(
            workspace=workspace,
            campaign=campaign,
            lead=lead,
            sequence_step=sequence_step,
            message_type=message_type,
            input_prompt=custom_instruction or user_prompt,
            generated_subject=parsed.get("subject"),
            generated_body=parsed.get("body"),
            variables_snapshot=variables,
            raw_response=raw_response,
            created_by=request.user,
        )

        created_step_data = None

        if create_sequence_step:
            if not campaign:
                return Response(
                    {
                        "status": "error",
                        "message": "campaign_id is required when create_sequence_step=true."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            next_step_number = (campaign.sequence_steps.order_by("-step_number").first().step_number + 1) if campaign.sequence_steps.exists() else 1

            step_type = "initial" if message_type == "initial" else "follow_up"

            new_step = CampaignSequenceStep.objects.create(
                campaign=campaign,
                step_number=next_step_number,
                step_type=step_type,
                delay_days=0 if next_step_number == 1 else campaign.follow_up_gap_days,
                subject=parsed.get("subject"),
                body=parsed.get("body"),
                is_ai_generated=True,
                is_active=True,
            )
            generated_message.sequence_step = new_step
            generated_message.save(update_fields=["sequence_step"])
            created_step_data = {
                "id": new_step.id,
                "step_number": new_step.step_number,
                "step_type": new_step.step_type,
                "subject": new_step.subject,
                "body": new_step.body,
            }

        return Response(
            {
                "status": "success",
                "message": "AI message generated successfully.",
                "data": {
                    "generated_message": AIGeneratedMessageDetailSerializer(generated_message).data,
                    "created_sequence_step": created_step_data,
                },
            },
            status=status.HTTP_201_CREATED
        )


class AIGeneratedMessageListAPIView(APIView, AIBaseMixin):
    def get(self, request):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = AIGeneratedMessage.objects.filter(workspace=workspace)

        message_type = request.GET.get("message_type", "").strip()
        campaign_id = request.GET.get("campaign_id", "").strip()
        lead_id = request.GET.get("lead_id", "").strip()

        if message_type:
            queryset = queryset.filter(message_type=message_type)

        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)

        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)

        queryset = queryset.order_by("-created_at")

        return Response(
            {
                "status": "success",
                "count": queryset.count(),
                "data": AIGeneratedMessageListSerializer(queryset, many=True).data,
            },
            status=status.HTTP_200_OK
        )


class AIGeneratedMessageDetailAPIView(APIView, AIBaseMixin):
    def get(self, request, message_id):
        workspace = self.get_workspace(request.user)
        if not workspace:
            return Response(
                {"status": "error", "message": "Workspace not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            message = AIGeneratedMessage.objects.get(id=message_id, workspace=workspace)
        except AIGeneratedMessage.DoesNotExist:
            return Response(
                {"status": "error", "message": "Generated message not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "status": "success",
                "data": AIGeneratedMessageDetailSerializer(message).data,
            },
            status=status.HTTP_200_OK
        )