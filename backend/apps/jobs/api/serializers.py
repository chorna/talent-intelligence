from rest_framework import serializers

from apps.jobs.choices import WorkMode
from apps.jobs.models import Application, Job


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
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        candidate = attrs.get(
            "candidate",
            getattr(self.instance, "candidate", None),
        )

        job = attrs.get(
            "job",
            getattr(self.instance, "job", None),
        )

        if candidate and job:
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
                        "candidate": (
                            "This candidate has already applied to this job."
                        ),
                    }
                )

        return attrs
