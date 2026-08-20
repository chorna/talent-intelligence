from rest_framework import serializers

from apps.candidates.models import CandidateFavorite


class CandidateFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateFavorite
        fields = [
            "id",
            "candidate",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
        ]
