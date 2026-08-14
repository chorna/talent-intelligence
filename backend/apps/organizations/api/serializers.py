from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.organizations.models import Organization
from apps.users.models import User


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
        )
        read_only_fields = fields


class OrganizationSerializer(serializers.ModelSerializer):
    recruiters = RecruiterSerializer(
        source="users",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "recruiters",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "recruiters",
            "created_at",
            "updated_at",
        )


class AddRecruiterSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        User = get_user_model()

        try:
            user = User.objects.get(
                email__iexact=value,
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User does not exist.",
            )

        if user.organization_id:
            raise serializers.ValidationError(
                "User already belongs to an organization.",
            )

        return value
