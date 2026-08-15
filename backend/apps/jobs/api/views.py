from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.models import Application, Job, JobSkill

from .serializers import (
    ApplicationSerializer,
    ApplicationStatusHistorySerializer,
    JobSerializer,
    JobSkillSerializer,
)


class JobViewSet(ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [HasOrganization]
    pagination_class = DefaultPagination
    filter_backends = [OrderingFilter]

    ordering_fields = [
        "title",
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Job.objects.filter(
                organization_id=self.request.user.organization_id,
            )
            .select_related(
                "organization",
                "created_by",
                "city",
            )
            .prefetch_related(
                "job_skills__skill",
            )
        )

        status_filter = self.request.query_params.get("status")
        work_mode = self.request.query_params.get("work_mode")
        employment_type = self.request.query_params.get("employment_type")
        city = self.request.query_params.get("city")
        country = self.request.query_params.get("country")
        search = self.request.query_params.get("search")
        skill = self.request.query_params.get("skill")
        skills = self.request.query_params.get("skills")

        if status_filter:
            queryset = queryset.filter(
                status__iexact=status_filter,
            )

        if work_mode:
            queryset = queryset.filter(
                work_mode__iexact=work_mode,
            )

        if employment_type:
            queryset = queryset.filter(
                employment_type__iexact=employment_type,
            )

        if city:
            queryset = queryset.filter(
                city__name__iexact=city,
            )

        if country:
            queryset = queryset.filter(
                city__country__code__iexact=country,
            )

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(job_skills__skill__name__icontains=search)
                | Q(job_skills__skill__slug__icontains=search),
            )

        if skill:
            queryset = queryset.filter(
                job_skills__skill__slug__iexact=skill,
            )

        if skills:
            skill_slugs = [
                value.strip() for value in skills.split(",") if value.strip()
            ]

            for skill_slug in skill_slugs:
                queryset = queryset.filter(
                    job_skills__skill__slug__iexact=skill_slug,
                )

        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="applications",
    )
    def applications(self, request, pk=None):
        job = self.get_object()

        applications = Application.objects.filter(
            job=job,
        ).select_related(
            "candidate",
            "candidate__city",
        )

        serializer = ApplicationSerializer(
            applications,
            many=True,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @applications.mapping.post
    def create_application(self, request, pk=None):
        job = self.get_object()

        serializer = ApplicationSerializer(
            data=request.data,
            context={
                "request": request,
                "job": job,
            },
        )

        serializer.is_valid(raise_exception=True)

        application = serializer.save()

        return Response(
            ApplicationSerializer(
                application,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="applications/(?P<application_id>[^/.]+)/status",
    )
    def update_application_status(
        self,
        request,
        pk=None,
        application_id=None,
    ):
        job = self.get_object()

        application = get_object_or_404(
            Application,
            id=application_id,
            job=job,
        )

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {
                    "status": [
                        "This field is required.",
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            application.transition_to(
                new_status,
                changed_by=request.user,
            )
        except ValidationError as exc:
            return Response(
                exc.message_dict,
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApplicationSerializer(
            application,
            context={"request": request},
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="applications/(?P<application_id>[^/.]+)/history",
    )
    def application_history(
        self,
        request,
        pk=None,
        application_id=None,
    ):
        job = self.get_object()

        application = get_object_or_404(
            Application,
            id=application_id,
            job=job,
        )

        history = application.status_history.select_related(
            "changed_by",
        )

        serializer = ApplicationStatusHistorySerializer(
            history,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="skills",
    )
    def skills(self, request, pk=None):
        job = self.get_object()

        job_skills = JobSkill.objects.filter(
            job=job,
        ).select_related(
            "skill",
        )

        serializer = JobSkillSerializer(
            job_skills,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @skills.mapping.post
    def create_skill(self, request, pk=None):
        job = self.get_object()

        serializer = JobSkillSerializer(
            data=request.data,
            context={
                "job": job,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        job_skill = serializer.save(
            job=job,
        )

        return Response(
            JobSkillSerializer(job_skill).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"skills/(?P<skill_id>[^/.]+)",
    )
    def delete_skill(
        self,
        request,
        pk=None,
        skill_id=None,
    ):
        job = self.get_object()

        job_skill = get_object_or_404(
            JobSkill,
            job=job,
            skill_id=skill_id,
        )

        job_skill.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
