import csv
import io

from rest_framework import serializers
from .models import Lead, LeadTag


class LeadTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadTag
        fields = ["id", "name"]


class LeadListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    tags = LeadTagSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "company_name",
            "company_website",
            "industry",
            "job_title",
            "status",
            "tags",
            "created_at",
            "updated_at",
        ]


class LeadDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    tags = LeadTagSerializer(many=True, read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "company_name",
            "company_website",
            "industry",
            "job_title",
            "linkedin_url",
            "city",
            "country",
            "status",
            "notes",
            "tags",
            "created_at",
            "updated_at",
        ]


class LeadCreateUpdateSerializer(serializers.ModelSerializer):
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )

    class Meta:
        model = Lead
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "company_name",
            "company_website",
            "industry",
            "job_title",
            "linkedin_url",
            "city",
            "country",
            "status",
            "notes",
            "tag_names",
        ]

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name is required.")
        return value.strip()

    def validate_email(self, value):
        return value.strip().lower()

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value.strip()

    def create(self, validated_data):
        tag_names = validated_data.pop("tag_names", [])
        workspace = self.context["workspace"]

        lead = Lead.objects.create(workspace=workspace, **validated_data)

        if tag_names:
            tags = []
            for tag_name in tag_names:
                cleaned_name = tag_name.strip()
                if cleaned_name:
                    tag, _ = LeadTag.objects.get_or_create(
                        workspace=workspace,
                        name=cleaned_name
                    )
                    tags.append(tag)
            lead.tags.set(tags)

        return lead

    def update(self, instance, validated_data):
        tag_names = validated_data.pop("tag_names", None)
        workspace = self.context["workspace"]

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tag_names is not None:
            tags = []
            for tag_name in tag_names:
                cleaned_name = tag_name.strip()
                if cleaned_name:
                    tag, _ = LeadTag.objects.get_or_create(
                        workspace=workspace,
                        name=cleaned_name
                    )
                    tags.append(tag)
            instance.tags.set(tags)

        return instance


class LeadCSVImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(".csv"):
            raise serializers.ValidationError("Only CSV files are allowed.")
        return value

    def parse_csv(self):
        uploaded_file = self.validated_data["file"]
        decoded_file = uploaded_file.read().decode("utf-8")
        csv_file = io.StringIO(decoded_file)
        reader = csv.DictReader(csv_file)
        return list(reader)