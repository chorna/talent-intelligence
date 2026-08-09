from rest_framework import serializers

from apps.candidates.models import Candidate
from apps.experiences.models import Experience
from apps.skills.models import Skill


class ExperienceSerializer(serializers.ModelSerializer):
    candidate = serializers.PrimaryKeyRelatedField(
        queryset=Candidate.objects.all(),
    )
    skills = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Skill.objects.all(),
        required=False,
    )

    class Meta:
        model = Experience
        fields = [
            "id",
            "candidate",
            "company_name",
            "job_title",
            "description",
            "location",
            "employment_type",
            "work_mode",
            "start_date",
            "end_date",
            "is_current",
            "skills",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_company_name(self, value):
        return " ".join(value.strip().split())

    def validate_job_title(self, value):
        return " ".join(value.strip().split())

    def validate_location(self, value):
        return " ".join(value.strip().split())

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            self.instance.start_date if self.instance else None,
        )
        end_date = attrs.get(
            "end_date",
            self.instance.end_date if self.instance else None,
        )
        is_current = attrs.get(
            "is_current",
            self.instance.is_current if self.instance else False,
        )

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError(
                {"end_date": ("End date cannot be earlier than start date.")}
            )

        if is_current and end_date:
            raise serializers.ValidationError(
                {"end_date": ("End date must be empty for a current experience.")}  # noqa: E501
            )

        return attrs
