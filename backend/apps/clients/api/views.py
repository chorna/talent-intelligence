from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.clients.api.serializers import (
    ClientContactSerializer,
    ClientDashboardSerializer,
    ClientNoteSerializer,
    ClientSerializer,
)
from apps.clients.models import Client
from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.api.serializers import JobSerializer
from apps.jobs.choices import ApplicationStatus, JobStatus
from apps.jobs.models import Application


@extend_schema(tags=["Clients"])
class ClientViewSet(ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [HasOrganization]
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["name"]

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

    @action(
        detail=True,
        methods=["get"],
        url_path="dashboard",
    )
    def dashboard(self, request, pk=None):
        client = self.get_object()

        jobs = client.jobs.all()

        job_summary = jobs.aggregate(
            total=Count("id"),
            active=Count(
                "id",
                filter=Q(status=JobStatus.OPEN),
            ),
        )

        applications = Application.objects.filter(
            job__client=client,
        )

        application_summary = applications.aggregate(
            total=Count("id"),
            applied=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.APPLIED,
                ),
            ),
            screening=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.SCREENING,
                ),
            ),
            interview=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.INTERVIEW,
                ),
            ),
            offer=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.OFFER,
                ),
            ),
            hired=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.HIRED,
                ),
            ),
            rejected=Count(
                "id",
                filter=Q(
                    status=ApplicationStatus.REJECTED,
                ),
            ),
        )

        data = {
            "client": client,
            "total_jobs": job_summary["total"],
            "active_jobs": job_summary["active"],
            "total_applications": application_summary["total"],
            "pipeline": {
                ApplicationStatus.APPLIED: application_summary["applied"],
                ApplicationStatus.SCREENING: application_summary["screening"],
                ApplicationStatus.INTERVIEW: application_summary["interview"],
                ApplicationStatus.OFFER: application_summary["offer"],
                ApplicationStatus.HIRED: application_summary["hired"],
                ApplicationStatus.REJECTED: application_summary["rejected"],
            },
        }

        serializer = ClientDashboardSerializer(data)

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["get"],
        url_path="notes",
    )
    def notes(self, request, pk=None):
        client = self.get_object()

        notes = client.notes.select_related(
            "author",
        )

        serializer = ClientNoteSerializer(
            notes,
            many=True,
        )

        return Response(serializer.data)

    @notes.mapping.post
    def create_note(self, request, pk=None):
        client = self.get_object()

        serializer = ClientNoteSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        note = serializer.save(
            client=client,
            author=request.user,
        )

        return Response(
            ClientNoteSerializer(note).data,
            status=status.HTTP_201_CREATED,
        )
