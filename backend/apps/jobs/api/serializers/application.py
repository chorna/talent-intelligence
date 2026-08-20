from rest_framework import serializers

from apps.jobs.models import Application, ApplicationStatusHistory


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
