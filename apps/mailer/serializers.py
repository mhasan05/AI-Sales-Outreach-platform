from rest_framework import serializers
from .models import SMTPSetting, EmailLog


class SMTPSettingSerializer(serializers.ModelSerializer):
    masked_password = serializers.SerializerMethodField()

    class Meta:
        model = SMTPSetting
        fields = [
            "id",
            "host",
            "port",
            "username",
            "password",
            "masked_password",
            "use_tls",
            "use_ssl",
            "from_email",
            "from_name",
            "reply_to_email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "masked_password", "created_at", "updated_at"]

    def get_masked_password(self, obj):
        if not obj.password:
            return ""
        if len(obj.password) <= 6:
            return "*" * len(obj.password)
        return f"{obj.password[:2]}{'*' * (len(obj.password) - 4)}{obj.password[-2:]}"


class SMTPSettingCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMTPSetting
        fields = [
            "host",
            "port",
            "username",
            "password",
            "use_tls",
            "use_ssl",
            "from_email",
            "from_name",
            "reply_to_email",
            "is_active",
        ]

    def validate_host(self, value):
        if not value.strip():
            raise serializers.ValidationError("SMTP host is required.")
        return value.strip()

    def validate_username(self, value):
        if not value.strip():
            raise serializers.ValidationError("SMTP username is required.")
        return value.strip()

    def validate_password(self, value):
        if not value.strip():
            raise serializers.ValidationError("SMTP password is required.")
        return value.strip()

    def validate_port(self, value):
        if value < 1:
            raise serializers.ValidationError("SMTP port must be greater than 0.")
        return value

    def validate(self, attrs):
        use_tls = attrs.get("use_tls")
        use_ssl = attrs.get("use_ssl")

        if use_tls and use_ssl:
            raise serializers.ValidationError("use_tls and use_ssl cannot both be true.")
        return attrs


class TestEmailSerializer(serializers.Serializer):
    to_email = serializers.EmailField()
    subject = serializers.CharField(max_length=255, required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)


class SendCampaignEmailSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    lead_id = serializers.IntegerField()
    sequence_step_id = serializers.IntegerField(required=False)
    subject = serializers.CharField(max_length=255, required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        sequence_step_id = attrs.get("sequence_step_id")
        subject = attrs.get("subject", "").strip()
        body = attrs.get("body", "").strip()

        if not sequence_step_id and (not subject or not body):
            raise serializers.ValidationError(
                "Either sequence_step_id or both subject and body are required."
            )
        return attrs


class EmailLogListSerializer(serializers.ModelSerializer):
    lead_email = serializers.EmailField(source="lead.email", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "to_email",
            "subject",
            "status",
            "lead_email",
            "campaign_name",
            "sent_at",
            "created_at",
        ]


class EmailLogDetailSerializer(serializers.ModelSerializer):
    lead_email = serializers.EmailField(source="lead.email", read_only=True)
    campaign_name = serializers.CharField(source="campaign.name", read_only=True)
    sequence_step_number = serializers.IntegerField(source="sequence_step.step_number", read_only=True)

    class Meta:
        model = EmailLog
        fields = [
            "id",
            "to_email",
            "subject",
            "body",
            "status",
            "error_message",
            "provider_message_id",
            "lead",
            "lead_email",
            "campaign",
            "campaign_name",
            "campaign_lead",
            "sequence_step",
            "sequence_step_number",
            "sent_at",
            "created_at",
        ]