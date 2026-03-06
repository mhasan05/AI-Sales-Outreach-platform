from rest_framework import serializers
from .models import Campaign, CampaignLead, CampaignSequenceStep
from apps.leads.models import Lead
from apps.leads.serializers import LeadListSerializer


class CampaignSequenceStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignSequenceStep
        fields = [
            "id",
            "step_number",
            "step_type",
            "delay_days",
            "subject",
            "body",
            "is_ai_generated",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CampaignLeadSerializer(serializers.ModelSerializer):
    lead = LeadListSerializer(read_only=True)

    class Meta:
        model = CampaignLead
        fields = [
            "id",
            "lead",
            "status",
            "last_contacted_at",
            "next_follow_up_at",
            "notes",
            "created_at",
        ]


class CampaignListSerializer(serializers.ModelSerializer):
    total_leads = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "description",
            "objective",
            "status",
            "daily_send_limit",
            "follow_up_gap_days",
            "start_date",
            "end_date",
            "total_leads",
            "total_steps",
            "created_at",
            "updated_at",
        ]

    def get_total_leads(self, obj):
        return obj.campaign_leads.count()

    def get_total_steps(self, obj):
        return obj.sequence_steps.count()


class CampaignDetailSerializer(serializers.ModelSerializer):
    total_leads = serializers.SerializerMethodField()
    total_steps = serializers.SerializerMethodField()
    campaign_leads = CampaignLeadSerializer(many=True, read_only=True)
    sequence_steps = CampaignSequenceStepSerializer(many=True, read_only=True)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "name",
            "description",
            "objective",
            "target_audience",
            "offer_summary",
            "status",
            "daily_send_limit",
            "follow_up_gap_days",
            "start_date",
            "end_date",
            "is_active",
            "total_leads",
            "total_steps",
            "campaign_leads",
            "sequence_steps",
            "created_at",
            "updated_at",
        ]

    def get_total_leads(self, obj):
        return obj.campaign_leads.count()

    def get_total_steps(self, obj):
        return obj.sequence_steps.count()


class CampaignCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "name",
            "description",
            "objective",
            "target_audience",
            "offer_summary",
            "status",
            "daily_send_limit",
            "follow_up_gap_days",
            "start_date",
            "end_date",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Campaign name is required.")
        return value.strip()

    def validate_daily_send_limit(self, value):
        if value < 1:
            raise serializers.ValidationError("Daily send limit must be at least 1.")
        return value

    def validate_follow_up_gap_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Follow up gap days cannot be negative.")
        return value

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be earlier than start date."})

        return attrs


class CampaignLeadAssignSerializer(serializers.Serializer):
    lead_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )

    def validate_lead_ids(self, value):
        if not value:
            raise serializers.ValidationError("lead_ids is required.")
        return value


class CampaignLeadStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignLead
        fields = [
            "status",
            "last_contacted_at",
            "next_follow_up_at",
            "notes",
        ]


class CampaignSequenceStepCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignSequenceStep
        fields = [
            "step_number",
            "step_type",
            "delay_days",
            "subject",
            "body",
            "is_ai_generated",
            "is_active",
        ]

    def validate_step_number(self, value):
        if value < 1:
            raise serializers.ValidationError("Step number must be at least 1.")
        return value

    def validate_delay_days(self, value):
        if value < 0:
            raise serializers.ValidationError("Delay days cannot be negative.")
        return value