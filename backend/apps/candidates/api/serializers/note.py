from rest_framework import serializers

from apps.candidates.models import CandidateNote


class CandidateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateNote
        fields = [
            "id",
            "candidate",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "candidate",
            "created_at",
            "updated_at",
        ]
