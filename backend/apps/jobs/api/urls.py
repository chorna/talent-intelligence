# backend/apps/jobs/api/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.application import ApplicationViewSet
from .views.feedback import FeedbackViewSet
from .views.job import JobViewSet
from .views.shortlist import ShortlistViewSet
from .views.skill import JobSkillViewSet
from .views.submission import SubmissionViewSet

# ------------------------------------------------------------------
# Jobs
# ------------------------------------------------------------------

job_router = DefaultRouter()

job_router.register(
    "jobs",
    JobViewSet,
    basename="job",
)


# ------------------------------------------------------------------
# Job-scoped resources
# ------------------------------------------------------------------

application_router = DefaultRouter()

application_router.register(
    "applications",
    ApplicationViewSet,
    basename="job-application",
)

shortlist_router = DefaultRouter()

shortlist_router.register(
    "shortlist",
    ShortlistViewSet,
    basename="job-shortlist",
)

submission_router = DefaultRouter()

submission_router.register(
    "submissions",
    SubmissionViewSet,
    basename="job-submission",
)

skill_router = DefaultRouter()

skill_router.register(
    "skills",
    JobSkillViewSet,
    basename="job-skill",
)

feedback_router = DefaultRouter()

feedback_router.register(
    "feedback",
    FeedbackViewSet,
    basename="submission-feedback",
)


urlpatterns = [
    path(
        "",
        include(job_router.urls),
    ),
    path(
        "jobs/<uuid:job_id>/",
        include(application_router.urls),
    ),
    path(
        "jobs/<uuid:job_id>/",
        include(shortlist_router.urls),
    ),
    path(
        "jobs/<uuid:job_id>/",
        include(submission_router.urls),
    ),
    path(
        "jobs/<uuid:job_id>/",
        include(skill_router.urls),
    ),
    path(
        "jobs/<uuid:job_id>/submissions/<uuid:submission_id>/",
        include(feedback_router.urls),
    ),
]
