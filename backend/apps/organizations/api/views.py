from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.permissions import IsSuperUser
from apps.organizations.models import Organization

from .serializers import (
    AddRecruiterSerializer,
    OrganizationSerializer,
    RecruiterSerializer,
)

User = get_user_model()


class OrganizationViewSet(ModelViewSet):
    queryset = Organization.objects.prefetch_related("users")
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.action == "me":
            return [IsAuthenticated()]

        return [IsSuperUser()]

    @action(
        detail=True,
        methods=["post"],
        url_path="recruiters",
    )
    def add_recruiter(self, request, pk=None):
        organization = self.get_object()

        serializer = AddRecruiterSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        recruiter = User.objects.get(
            email__iexact=serializer.validated_data["email"],
        )

        if recruiter.organization_id:
            return Response(
                {
                    "detail": ("User already belongs to an organization."),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        recruiter.organization = organization
        recruiter.save(
            update_fields=["organization"],
        )

        return Response(
            RecruiterSerializer(recruiter).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if not request.user.organization_id:
            return Response(
                {
                    "detail": "User does not belong to an organization.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(
            request.user.organization,
        )

        return Response(serializer.data)
