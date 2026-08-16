from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.clients.api.serializers import (
    ClientContactSerializer,
    ClientSerializer,
)
from apps.clients.models import Client
from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.api.serializers import JobSerializer


@extend_schema(tags=["Clients"])
class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [HasOrganization]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = (
            Client.objects.filter(
                organization_id=self.request.user.organization_id,
            )
            .select_related(
                "organization",
            )
            .prefetch_related(
                "contacts",
            )
        )

        status_filter = self.request.query_params.get(
            "status",
        )
        search = self.request.query_params.get(
            "search",
        )

        if status_filter:
            queryset = queryset.filter(
                status__iexact=status_filter,
            )

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(website__icontains=search),
            )

        return queryset.distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.request.user.organization
        return context

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="contacts",
    )
    def contacts(self, request, pk=None):
        client = self.get_object()

        contacts = client.contacts.all()

        serializer = ClientContactSerializer(
            contacts,
            many=True,
            context=self.get_serializer_context(),
        )

        return Response(serializer.data)

    @contacts.mapping.post
    def create_contact(self, request, pk=None):
        client = self.get_object()

        serializer = ClientContactSerializer(
            data=request.data,
            context=self.get_serializer_context(),
        )

        serializer.is_valid(
            raise_exception=True,
        )

        contact = serializer.save(
            client=client,
        )

        return Response(
            ClientContactSerializer(contact).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="jobs",
    )
    def jobs(self, request, pk=None):
        client = self.get_object()

        jobs = client.jobs.all()

        serializer = JobSerializer(
            jobs,
            many=True,
            context=self.get_serializer_context(),
        )

        return Response(
            serializer.data,
        )
