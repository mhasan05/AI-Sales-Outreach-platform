from rest_framework import serializers


class DashboardSummarySerializer(serializers.Serializer):
    total_leads = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    total_ai_messages = serializers.IntegerField()
    total_sent_emails = serializers.IntegerField()
    total_failed_emails = serializers.IntegerField()
    total_pending_emails = serializers.IntegerField()
    interested_leads = serializers.IntegerField()
    meetings_booked = serializers.IntegerField()
    active_campaigns = serializers.IntegerField()
    paused_campaigns = serializers.IntegerField()
    completed_campaigns = serializers.IntegerField()


class RecentActivitySerializer(serializers.Serializer):
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    created_at = serializers.DateTimeField()


class CampaignPerformanceSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    campaign_name = serializers.CharField()
    campaign_status = serializers.CharField()
    total_assigned_leads = serializers.IntegerField()
    contacted = serializers.IntegerField()
    replied = serializers.IntegerField()
    interested = serializers.IntegerField()
    meetings_booked = serializers.IntegerField()
    completed = serializers.IntegerField()
    sent_emails = serializers.IntegerField()
    failed_emails = serializers.IntegerField()


class LeadStatusBreakdownSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class EmailStatusBreakdownSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()