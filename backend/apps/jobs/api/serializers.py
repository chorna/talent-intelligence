from rest_framework import serializers

from apps.jobs.choices import WorkMode
from apps.jobs.models import Application, ApplicationStatusHistory, Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "description",
            "city",
            "employment_type",
            "work_mode",
            "organization",
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


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id",
            "candidate",
            "job",
            "status",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "job",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        job = self.context.get("job")

        if job is None:
            raise serializers.ValidationError(
                "Job is required.",
            )

        candidate = attrs["candidate"]

        queryset = Application.objects.filter(
            candidate=candidate,
            job=job,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "candidate": ("This candidate has already applied to this job."),
                }
            )

        return attrs

    def create(self, validated_data):
        job = self.context["job"]
        changed_by = self.context["request"].user

        return Application.create_with_history(
            candidate=validated_data["candidate"],
            job=job,
            notes=validated_data.get("notes", ""),
            changed_by=changed_by,
        )


class ApplicationStatusHistorySerializer(
    serializers.ModelSerializer,
):
    changed_by = serializers.EmailField(
        source="changed_by.email",
        read_only=True,
    )

    class Meta:
        model = ApplicationStatusHistory
        fields = [
            "id",
            "from_status",
            "to_status",
            "changed_by",
            "created_at",
        ]
