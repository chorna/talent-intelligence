from rest_framework.routers import DefaultRouter

from .views import CandidateImportViewSet, CandidateViewSet

router = DefaultRouter()

router.register(
    "candidates",
    CandidateViewSet,
    basename="candidate",
)

router.register(
    "candidate-imports",
    CandidateImportViewSet,
    basename="candidate-import",
)

urlpatterns = router.urls
