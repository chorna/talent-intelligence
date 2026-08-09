from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class JWTAuthenticationTests(APITestCase):
    def setUp(self):
        self.email = "christian@example.com"
        self.password = "secret123"

        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            first_name="Christian",
            last_name="Horna",
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_password_fails(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.email,
                "password": "wrong-password",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_login_with_invalid_email_fails(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "unknown@example.com",
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            reverse("token_refresh"),
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)

    def test_refresh_with_invalid_token_fails(self):
        response = self.client.post(
            reverse("token_refresh"),
            {
                "refresh": "invalid-token",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_request_can_access_candidates(self):
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        response = self.client.get("/api/candidates/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_unauthenticated_request_cannot_access_candidates(self):
        response = self.client.get("/api/candidates/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
