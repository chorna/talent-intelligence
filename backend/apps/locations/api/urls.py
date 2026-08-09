from rest_framework.routers import DefaultRouter

from .views import CityViewSet, CountryViewSet

router = DefaultRouter()

router.register(
    "countries",
    CountryViewSet,
    basename="country",
)

router.register(
    "cities",
    CityViewSet,
    basename="city",
)

urlpatterns = router.urls
