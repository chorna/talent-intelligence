from rest_framework import status
from rest_framework.test import APITestCase

from apps.organizations.models import Organization
from apps.users.models import User


class OrganizationAPITests(APITestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.other_organization = Organization.objects.create(
            name="Other Company",
        )

        self.superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="testpassword123",
        )

        self.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.unassigned_user = User.objects.create_user(
            email="unassigned@example.com",
            password="testpassword123",
        )

        self.other_recruiter = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
            organization=self.other_organization,
        )

        self.url = "/api/organizations/"

    def test_superuser_can_list_organizations(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_superuser_can_create_organization(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            self.url,
            {
                "name": "New Company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Organization.objects.filter(
                name="New Company",
            ).exists(),
        )

    def test_recruiter_cannot_create_organization(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            self.url,
            {
                "name": "Unauthorized Company",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_superuser_can_add_recruiter(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            f"{self.url}{self.organization.id}/recruiters/",
            {
                "email": self.unassigned_user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.unassigned_user.refresh_from_db()

        self.assertEqual(
            self.unassigned_user.organization,
            self.organization,
        )

    def test_superuser_cannot_add_user_from_another_organization(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            f"{self.url}{self.organization.id}/recruiters/",
            {
                "email": self.other_recruiter.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.other_recruiter.refresh_from_db()

        self.assertEqual(
            self.other_recruiter.organization,
            self.other_organization,
        )

    def test_superuser_cannot_add_nonexistent_recruiter(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            f"{self.url}{self.organization.id}/recruiters/",
            {
                "email": "doesnotexist@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_add_recruiter_email_is_case_insensitive(self):
        self.client.force_authenticate(
            user=self.superuser,
        )

        response = self.client.post(
            f"{self.url}{self.organization.id}/recruiters/",
            {
                "email": "UNASSIGNED@EXAMPLE.COM",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.unassigned_user.refresh_from_db()

        self.assertEqual(
            self.unassigned_user.organization,
            self.organization,
        )

    def test_recruiter_cannot_add_recruiter(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.post(
            f"{self.url}{self.organization.id}/recruiters/",
            {
                "email": self.unassigned_user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.unassigned_user.refresh_from_db()

        self.assertIsNone(
            self.unassigned_user.organization,
        )

    def test_recruiter_can_get_own_organization(self):
        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}me/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            str(self.organization.id),
        )

        self.assertEqual(
            response.data["name"],
            "ACME Technologies",
        )

    def test_me_returns_organization_recruiters(self):
        second_recruiter = User.objects.create_user(
            email="second@example.com",
            password="testpassword123",
            organization=self.organization,
        )

        self.client.force_authenticate(
            user=self.recruiter,
        )

        response = self.client.get(
            f"{self.url}me/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        emails = {recruiter["email"] for recruiter in response.data["recruiters"]}

        self.assertEqual(
            emails,
            {
                self.recruiter.email,
                second_recruiter.email,
            },
        )

    def test_user_without_organization_cannot_get_me(self):
        self.client.force_authenticate(
            user=self.unassigned_user,
        )

        response = self.client.get(
            f"{self.url}me/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_anonymous_user_cannot_get_organization(self):
        response = self.client.get(
            f"{self.url}me/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
