# Create your tests here.
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.locations.models import City, Country
from apps.users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="recruiter@example.com",
        password="secure-password",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def countries(db):
    peru = Country.objects.create(
        name="Peru",
        code="PE",
    )

    chile = Country.objects.create(
        name="Chile",
        code="CL",
    )

    return peru, chile


@pytest.fixture
def cities(countries):
    peru, chile = countries

    lima = City.objects.create(
        country=peru,
        name="Lima",
    )

    arequipa = City.objects.create(
        country=peru,
        name="Arequipa",
    )

    santiago = City.objects.create(
        country=chile,
        name="Santiago",
    )

    return lima, arequipa, santiago


@pytest.mark.django_db
class TestCountryAPI:
    def test_list_countries(
        self,
        authenticated_client,
        countries,
    ):
        response = authenticated_client.get(
            "/api/locations/countries/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_country(
        self,
        authenticated_client,
        countries,
    ):
        peru, _ = countries

        response = authenticated_client.get(
            f"/api/locations/countries/{peru.id}/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(peru.id)
        assert response.data["name"] == "Peru"
        assert response.data["code"] == "PE"

    def test_search_country(
        self,
        authenticated_client,
        countries,
    ):
        response = authenticated_client.get(
            "/api/locations/countries/",
            {"search": "Peru"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Peru"

    def test_inactive_country_is_not_returned(
        self,
        authenticated_client,
        countries,
    ):
        peru, _ = countries

        peru.is_active = False
        peru.save()

        response = authenticated_client.get(
            "/api/locations/countries/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Chile"

    def test_unauthenticated_user_cannot_list_countries(
        self,
        api_client,
        countries,
    ):
        response = api_client.get(
            "/api/locations/countries/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCityAPI:
    def test_list_cities(
        self,
        authenticated_client,
        cities,
    ):
        response = authenticated_client.get(
            "/api/locations/cities/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_retrieve_city(
        self,
        authenticated_client,
        cities,
    ):
        lima, _, _ = cities

        response = authenticated_client.get(
            f"/api/locations/cities/{lima.id}/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Lima"
        assert response.data["country"]["name"] == "Peru"
        assert response.data["country"]["code"] == "PE"

    def test_search_city(
        self,
        authenticated_client,
        cities,
    ):
        response = authenticated_client.get(
            "/api/locations/cities/",
            {"search": "Lima"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Lima"

    def test_filter_cities_by_country(
        self,
        authenticated_client,
        countries,
        cities,
    ):
        peru, _ = countries

        response = authenticated_client.get(
            "/api/locations/cities/",
            {"country": peru.id},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        names = {city["name"] for city in response.data}

        assert names == {
            "Lima",
            "Arequipa",
        }

    def test_search_cities_by_country_name(
        self,
        authenticated_client,
        cities,
    ):
        response = authenticated_client.get(
            "/api/locations/cities/",
            {"search": "Peru"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_inactive_city_is_not_returned(
        self,
        authenticated_client,
        cities,
    ):
        lima, _, _ = cities

        lima.is_active = False
        lima.save()

        response = authenticated_client.get(
            "/api/locations/cities/",
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        names = {city["name"] for city in response.data}

        assert "Lima" not in names

    def test_unauthenticated_user_cannot_list_cities(
        self,
        api_client,
        cities,
    ):
        response = api_client.get(
            "/api/locations/cities/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
