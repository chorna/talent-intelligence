from drf_spectacular.utils import extend_schema
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.locations.models import City, Country

from .serializers import CitySerializer, CountrySerializer


@extend_schema(tags=["Countries"])
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.filter(
        is_active=True,
    )
    serializer_class = CountrySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "code",
    ]


@extend_schema(tags=["Cities"])
class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.filter(
        is_active=True,
    )
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "name",
        "country__name",
        "country__code",
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        country_id = self.request.query_params.get("country")

        if country_id:
            queryset = queryset.filter(
                country_id=country_id,
            )

        return queryset
