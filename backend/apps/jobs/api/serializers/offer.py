from rest_framework import serializers

from apps.jobs.models import Offer


class OfferSerializer(serializers.ModelSerializer):
    submission = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Offer
        fields = [
            "id",
            "submission",
            "salary",
            "currency",
            "status",
            "offered_at",
            "expires_at",
            "responded_at",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "submission",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        offered_at = attrs.get("offered_at")
        expires_at = attrs.get("expires_at")

        if offered_at and expires_at and expires_at <= offered_at:
            raise serializers.ValidationError(
                {
                    "expires_at": (
                        "Expiration date must be later than the offer date."
                    ),
                }
            )

        return attrs
