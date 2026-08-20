from rest_framework import serializers

from apps.jobs.models import ClientCandidateFeedback


class ClientCandidateFeedbackSerializer(
    serializers.ModelSerializer,
):
    created_by = serializers.EmailField(
        source="created_by.email",
        read_only=True,
    )

    class Meta:
        model = ClientCandidateFeedback
        fields = (
            "id",
            "submission",
            "decision",
            "comments",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "submission",
            "created_by",
            "created_at",
            "updated_at",
        )
