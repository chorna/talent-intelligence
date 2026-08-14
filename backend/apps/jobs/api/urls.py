from rest_framework.routers import DefaultRouter

from .views import ApplicationViewSet, JobViewSet

router = DefaultRouter()

router.register(
    "jobs",
    JobViewSet,
    basename="job",
)

router.register(
    "applications",
    ApplicationViewSet,
    basename="application",
)

urlpatterns = router.urls
