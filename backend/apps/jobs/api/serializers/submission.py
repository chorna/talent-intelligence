from rest_framework import serializers

from apps.jobs.models import CandidateShortlist, CandidateSubmission


class CandidateSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateSubmission
        fields = (
            "id",
            "job",
            "candidate",
            "client",
            "submitted_by",
            "status",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "job",
            "client",
            "submitted_by",
            "status",
            "created_at",
            "updated_at",
        )

    def validate_candidate(self, candidate):
        job = self.context.get("job")

        if job is None:
            raise serializers.ValidationError(
                "Job is required.",
            )

        if not CandidateShortlist.objects.filter(
            job=job,
            candidate=candidate,
        ).exists():
            raise serializers.ValidationError(
                "Candidate must be in the job shortlist before submission.",
            )

        if CandidateSubmission.objects.filter(
            job=job,
            candidate=candidate,
        ).exists():
            raise serializers.ValidationError(
                "This candidate has already been submitted for this job.",
            )

        return candidate
