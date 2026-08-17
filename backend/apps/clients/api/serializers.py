from rest_framework import serializers

from apps.clients.models import Client, ClientContact, ClientNote


class ClientContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContact
        fields = [
            "id",
            "client",
            "name",
            "email",
            "phone",
            "position",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "client",
            "created_at",
            "updated_at",
        ]


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "organization",
            "name",
            "website",
            "description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "organization",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        organization = self.context.get("organization")

        if organization is None:
            raise serializers.ValidationError(
                "Organization is required.",
            )

        name = attrs.get("name")

        queryset = Client.objects.filter(
            organization=organization,
            name=name,
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "name": (
                        "A client with this name already exists in this organization."
                    ),
                }
            )

        return attrs


class ClientDashboardSerializer(serializers.Serializer):
    client = serializers.SerializerMethodField()
    total_jobs = serializers.IntegerField()
    active_jobs = serializers.IntegerField()
    total_applications = serializers.IntegerField()
    pipeline = serializers.DictField()

    def get_client(self, obj):
        client = obj["client"]

        return {
            "id": str(client.id),
            "name": client.name,
        }


class ClientNoteSerializer(serializers.ModelSerializer):
    author = serializers.EmailField(
        source="author.email",
        read_only=True,
    )

    class Meta:
        model = ClientNote
        fields = [
            "id",
            "author",
            "content",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_at",
            "updated_at",
        ]
