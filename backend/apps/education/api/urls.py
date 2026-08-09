from rest_framework.routers import DefaultRouter

from .views import EducationViewSet

router = DefaultRouter()
router.register(
    "education",
    EducationViewSet,
    basename="education",
)

urlpatterns = router.urls
