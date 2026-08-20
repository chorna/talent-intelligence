from rest_framework import serializers

from apps.jobs.models import CandidateShortlist


class CandidateShortlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateShortlist
        fields = (
            "id",
            "candidate",
            "notes",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_by",
            "created_at",
            "updated_at",
        )

    def validate_candidate(self, candidate):
        job = self.context.get("job")

        if job is None:
            raise serializers.ValidationError(
                "Job is required.",
            )

        if CandidateShortlist.objects.filter(
            job=job,
            candidate=candidate,
        ).exists():
            raise serializers.ValidationError(
                "This candidate is already in the shortlist.",
            )

        return candidate
