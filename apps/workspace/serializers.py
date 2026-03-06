from rest_framework import serializers
from .models import Workspace


class WorkspaceSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(source="owner.id", read_only=True)
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Workspace
        fields = [
            "id",
            "owner_id",
            "owner_email",
            "company_name",
            "company_website",
            "business_type",
            "industry",
            "company_size",
            "sender_name",
            "sender_email",
            "sender_position",
            "business_description",
            "product_service_summary",
            "target_audience",
            "unique_selling_points",
            "default_email_tone",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner_id",
            "owner_email",
            "is_active",
            "created_at",
            "updated_at",
        ]


class WorkspaceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = [
            "company_name",
            "company_website",
            "business_type",
            "industry",
            "company_size",
            "sender_name",
            "sender_email",
            "sender_position",
            "business_description",
            "product_service_summary",
            "target_audience",
            "unique_selling_points",
            "default_email_tone",
        ]

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value

    def validate_sender_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Sender name is required.")
        return value