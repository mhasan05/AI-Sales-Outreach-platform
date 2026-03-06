from rest_framework import serializers
from .models import AIProviderSetting, AIGeneratedMessage


class AIProviderSettingSerializer(serializers.ModelSerializer):
    masked_api_key = serializers.SerializerMethodField()

    class Meta:
        model = AIProviderSetting
        fields = [
            "id",
            "provider",
            "api_key",
            "masked_api_key",
            "model_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "masked_api_key", "created_at", "updated_at"]

    def get_masked_api_key(self, obj):
        if not obj.api_key:
            return ""
        if len(obj.api_key) <= 8:
            return "*" * len(obj.api_key)
        return f"{obj.api_key[:4]}{'*' * (len(obj.api_key) - 8)}{obj.api_key[-4:]}"


class AIProviderSettingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIProviderSetting
        fields = [
            "provider",
            "api_key",
            "model_name",
            "is_active",
        ]

    def validate_api_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("API key is required.")
        return value.strip()


class AIGeneratedMessageListSerializer(serializers.ModelSerializer):
    lead_email = serializers.EmailField(source="lead.email", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)

    class Meta:
        model = AIGeneratedMessage
        fields = [
            "id",
            "message_type",
            "lead_email",
            "campaign_name",
            "generated_subject",
            "created_at",
        ]


class AIGeneratedMessageDetailSerializer(serializers.ModelSerializer):
    lead_email = serializers.EmailField(source="lead.email", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    sequence_step_number = serializers.IntegerField(source="sequence_step.step_number", read_only=True)

    class Meta:
        model = AIGeneratedMessage
        fields = [
            "id",
            "message_type",
            "lead",
            "lead_email",
            "campaign",
            "campaign_name",
            "sequence_step",
            "sequence_step_number",
            "input_prompt",
            "generated_subject",
            "generated_body",
            "variables_snapshot",
            "raw_response",
            "created_at",
        ]


class GenerateMessageSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField(required=False)
    lead_id = serializers.IntegerField(required=False)
    sequence_step_id = serializers.IntegerField(required=False)
    message_type = serializers.ChoiceField(choices=["initial", "follow_up", "custom"])
    custom_instruction = serializers.CharField(required=False, allow_blank=True)
    create_sequence_step = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        message_type = attrs.get("message_type")

        if message_type in ["initial", "follow_up"] and not attrs.get("lead_id"):
            raise serializers.ValidationError({"lead_id": "lead_id is required for initial/follow_up generation."})

        return attrs