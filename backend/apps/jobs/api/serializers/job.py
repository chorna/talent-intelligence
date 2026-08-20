from rest_framework import serializers

from apps.jobs.api.serializers.skill import JobSkillSerializer
from apps.jobs.choices import WorkMode
from apps.jobs.models import Job


class JobSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            "id",
            "client",
            "title",
            "description",
            "city",
            "employment_type",
            "work_mode",
            "organization",
            "skills",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "organization",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_client(self, client):
        organization = self.context.get("organization")

        if organization is None:
            raise serializers.ValidationError(
                "Organization is required.",
            )

        if client.organization_id != organization.id:
            raise serializers.ValidationError(
                "Client does not belong to your organization.",
            )

        return client

    def validate(self, attrs):
        work_mode = attrs.get(
            "work_mode",
            getattr(self.instance, "work_mode", None),
        )

        city = attrs.get(
            "city",
            getattr(self.instance, "city", None),
        )

        if work_mode == WorkMode.REMOTE and city is not None:
            raise serializers.ValidationError(
                {
                    "city": "Remote jobs cannot have a city.",
                }
            )

        if (
            work_mode
            in {
                WorkMode.HYBRID,
                WorkMode.ON_SITE,
            }
            and city is None
        ):
            raise serializers.ValidationError(
                {
                    "city": "City is required for hybrid and on-site jobs.",
                }
            )

        return attrs

    def get_skills(self, obj):
        return JobSkillSerializer(
            obj.job_skills.all(),
            many=True,
        ).data
