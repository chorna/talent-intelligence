from rest_framework import serializers

from apps.jobs.models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    interviewer = serializers.CharField(
        required=True,
        allow_blank=False,
    )

    class Meta:
        model = Interview
        fields = [
            "id",
            "submission",
            "scheduled_at",
            "status",
            "interviewer",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_submission(self, submission):
        job = self.context["job"]

        if submission.job_id != job.id:
            raise serializers.ValidationError(
                "Submission does not belong to this job.",
            )

        return submission
