import pytest
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


@pytest.mark.django_db
class TestUserMeAPI:
    def setup_method(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="christian@example.com",
            password="secure-password",
            first_name="Christian",
            last_name="Horna",
        )

        self.url = "/api/users/me/"

    def test_authenticated_user_can_retrieve_me(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(self.user.id)
        assert response.data["email"] == "christian@example.com"
        assert response.data["first_name"] == "Christian"
        assert response.data["last_name"] == "Horna"

    def test_unauthenticated_user_cannot_retrieve_me(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_update_first_name(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {
                "first_name": "Chris",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()

        assert self.user.first_name == "Chris"
        assert response.data["first_name"] == "Chris"

    def test_authenticated_user_can_update_last_name(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {
                "last_name": "H.",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()

        assert self.user.last_name == "H."
        assert response.data["last_name"] == "H."

    def test_email_cannot_be_updated(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.url,
            {
                "email": "new@example.com",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        self.user.refresh_from_db()

        assert self.user.email == "christian@example.com"
        assert response.data["email"] == "christian@example.com"

    def test_password_is_not_returned(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "password" not in response.data

    def test_authenticated_user_can_change_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/users/change-password/",
            {
                "current_password": "secure-password",
                "new_password": "new-secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"detail": "Password changed successfully."}

        self.user.refresh_from_db()

        assert self.user.check_password("new-secure-password")
        assert not self.user.check_password("secure-password")

    def test_change_password_requires_current_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/users/change-password/",
            {
                "current_password": "wrong-password",
                "new_password": "new-secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "current_password" in response.data

        self.user.refresh_from_db()

        assert self.user.check_password("secure-password")

    def test_change_password_requires_different_password(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/users/change-password/",
            {
                "current_password": "secure-password",
                "new_password": "secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "new_password" in response.data

    def test_unauthenticated_user_cannot_change_password(self):
        response = self.client.post(
            "/api/users/change-password/",
            {
                "current_password": "secure-password",
                "new_password": "new-secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_logout(self):
        self.client.force_authenticate(user=self.user)

        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/users/logout/",
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_revokes_refresh_token(self):
        self.client.force_authenticate(user=self.user)

        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)

        logout_response = self.client.post(
            "/api/users/logout/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        assert logout_response.status_code == status.HTTP_204_NO_CONTENT

        refresh_response = self.client.post(
            "/api/auth/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_with_invalid_refresh_token_returns_401(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/users/logout/",
            {
                "refresh": "invalid-refresh-token",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_user_cannot_logout(self):
        refresh = RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/users/logout/",
            {
                "refresh": str(refresh),
            },
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_requires_refresh_token(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/users/logout/",
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "refresh" in response.data

    def test_register_user(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "email": "new@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "secure-password",
                "password_confirm": "secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(
            email="new@example.com",
        )

        assert user.first_name == "New"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.check_password("secure-password")

    def test_register_user_does_not_return_password(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "email": "new@example.com",
                "password": "secure-password",
                "password_confirm": "secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert "password_confirm" not in response.data

    def test_register_user_requires_matching_passwords(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "email": "new@example.com",
                "password": "secure-password",
                "password_confirm": "different-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_user_with_duplicate_email(self):
        User.objects.create_user(
            email="existing@example.com",
            password="secure-password",
        )

        response = self.client.post(
            "/api/users/register/",
            {
                "email": "existing@example.com",
                "password": "secure-password",
                "password_confirm": "secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_user_does_not_require_authentication(self):
        response = self.client.post(
            "/api/users/register/",
            {
                "email": "anonymous@example.com",
                "password": "secure-password",
                "password_confirm": "secure-password",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
