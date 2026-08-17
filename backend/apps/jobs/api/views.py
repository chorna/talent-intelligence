from django.core.exceptions import ValidationError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.core.pagination import DefaultPagination
from apps.core.permissions import HasOrganization
from apps.jobs.choices import ApplicationStatus, JobStatus
from apps.jobs.models import (
    Application,
    CandidateShortlist,
    CandidateSubmission,
    Job,
    JobSkill,
)

from .serializers import (
    ApplicationSerializer,
    ApplicationStatusHistorySerializer,
    CandidateShortlistSerializer,
    CandidateSubmissionSerializer,
    JobSerializer,
    JobSkillSerializer,
)


@extend_schema(tags=["Jobs"])
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
                "client",
            )
            .prefetch_related(
                "job_skills__skill",
            )
        )

        if self.action != "list":
            return queryset

        status_filter = self.request.query_params.get("status")
        work_mode = self.request.query_params.get("work_mode")
        employment_type = self.request.query_params.get(
            "employment_type",
        )
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
                Q(title__icontains=search) | Q(description__icontains=search),
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

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context["organization"] = self.request.user.organization

        return context

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

        status_filter = request.query_params.get("status")
        candidate = request.query_params.get("candidate")
        search = request.query_params.get("search")

        if status_filter:
            applications = applications.filter(
                status__iexact=status_filter,
            )

        if candidate:
            applications = applications.filter(
                candidate_id=candidate,
            )

        if search:
            applications = applications.filter(
                Q(candidate__first_name__icontains=search)
                | Q(candidate__last_name__icontains=search)
                | Q(candidate__email__icontains=search)
            )

        applications = applications.distinct()

        ordering = request.query_params.get(
            "ordering",
            "-created_at",
        )

        allowed_ordering = {
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "status",
            "-status",
        }

        if ordering in allowed_ordering:
            applications = applications.order_by(ordering)

        page = self.paginate_queryset(applications)

        if page is not None:
            serializer = ApplicationSerializer(
                page,
                many=True,
                context={"request": request},
            )

            return self.get_paginated_response(
                serializer.data,
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

    @action(
        detail=True,
        methods=["patch"],
        url_path="applications/(?P<application_id>[^/.]+)/notes",
    )
    def update_application_notes(
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

        notes = request.data.get("notes")

        if notes is None:
            return Response(
                {
                    "notes": [
                        "This field is required.",
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.notes = notes
        application.save(
            update_fields=[
                "notes",
                "updated_at",
            ],
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
        url_path="applications/summary",
    )
    def applications_summary(self, request, pk=None):
        job = self.get_object()

        summary = (
            Application.objects.filter(
                job=job,
            )
            .values("status")
            .annotate(total=Count("id"))
        )

        pipeline = {status_value: 0 for status_value, _ in ApplicationStatus.choices}

        for item in summary:
            pipeline[item["status"]] = item["total"]

        return Response(
            {
                "total": sum(pipeline.values()),
                "pipeline": pipeline,
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="dashboard",
    )
    def dashboard(self, request):
        organization_id = request.user.organization_id

        jobs = Job.objects.filter(
            organization_id=organization_id,
        )

        applications = Application.objects.filter(
            job__organization_id=organization_id,
        )

        pipeline = {status_value: 0 for status_value in ApplicationStatus.values}

        pipeline_summary = applications.values("status").annotate(total=Count("id"))

        for item in pipeline_summary:
            pipeline[item["status"]] = item["total"]

        total_applications = applications.count()

        hired_rate = (
            round(
                pipeline[ApplicationStatus.HIRED] / total_applications * 100,
                2,
            )
            if total_applications
            else 0
        )

        rejected_rate = (
            round(
                pipeline[ApplicationStatus.REJECTED] / total_applications * 100,
                2,
            )
            if total_applications
            else 0
        )

        return Response(
            {
                "total_jobs": jobs.count(),
                "active_jobs": jobs.filter(
                    status=JobStatus.OPEN,
                ).count(),
                "total_applications": total_applications,
                "pipeline": pipeline,
                "metrics": {
                    "hired_rate": hired_rate,
                    "rejected_rate": rejected_rate,
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="shortlist",
    )
    def shortlist(self, request, pk=None):
        job = self.get_object()

        shortlist = job.shortlist.select_related(
            "candidate",
            "created_by",
        )

        serializer = CandidateShortlistSerializer(
            shortlist,
            many=True,
        )

        return Response(serializer.data)

    @shortlist.mapping.post
    def create_shortlist_candidate(self, request, pk=None):
        job = self.get_object()

        serializer = CandidateShortlistSerializer(
            data=request.data,
            context={
                "request": request,
                "job": job,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        shortlist = serializer.save(
            job=job,
            created_by=request.user,
        )

        return Response(
            CandidateShortlistSerializer(shortlist).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"shortlist/(?P<shortlist_id>[^/.]+)",
    )
    def remove_from_shortlist(
        self,
        request,
        pk=None,
        shortlist_id=None,
    ):
        job = self.get_object()

        shortlist = get_object_or_404(
            CandidateShortlist,
            id=shortlist_id,
            job=job,
        )

        shortlist.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="submissions",
    )
    def submissions(self, request, pk=None):
        job = self.get_object()

        submissions = job.submissions.select_related(
            "candidate",
            "client",
            "submitted_by",
        )

        serializer = CandidateSubmissionSerializer(
            submissions,
            many=True,
        )

        return Response(serializer.data)

    @submissions.mapping.post
    def create_submission(self, request, pk=None):
        job = self.get_object()

        serializer = CandidateSubmissionSerializer(
            data=request.data,
            context={
                "request": request,
                "job": job,
            },
        )

        serializer.is_valid(
            raise_exception=True,
        )

        submission = serializer.save(
            job=job,
            client=job.client,
            submitted_by=request.user,
        )

        return Response(
            CandidateSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["delete"],
        url_path=r"submissions/(?P<submission_id>[^/.]+)",
    )
    def remove_submission(
        self,
        request,
        pk=None,
        submission_id=None,
    ):
        job = self.get_object()

        submission = get_object_or_404(
            CandidateSubmission,
            id=submission_id,
            job=job,
        )

        submission.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
