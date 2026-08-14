# Create your tests here.
from django.test import TestCase

from apps.organizations.models import Organization
from apps.users.models import User


class OrganizationModelTests(TestCase):
    def test_create_organization(self):
        organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.assertIsNotNone(
            organization.id,
        )

        self.assertEqual(
            organization.name,
            "ACME Technologies",
        )

    def test_organization_str(self):
        organization = Organization.objects.create(
            name="ACME Technologies",
        )

        self.assertEqual(
            str(organization),
            "ACME Technologies",
        )

    def test_user_belongs_to_organization(self):
        organization = Organization.objects.create(
            name="ACME Technologies",
        )

        user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
            organization=organization,
        )

        self.assertEqual(
            user.organization,
            organization,
        )

    def test_organization_has_multiple_users(self):
        organization = Organization.objects.create(
            name="ACME Technologies",
        )

        user_1 = User.objects.create_user(
            email="recruiter1@example.com",
            password="testpassword123",
            organization=organization,
        )

        user_2 = User.objects.create_user(
            email="recruiter2@example.com",
            password="testpassword123",
            organization=organization,
        )

        self.assertEqual(
            organization.users.count(),
            2,
        )

        self.assertIn(
            user_1,
            organization.users.all(),
        )

        self.assertIn(
            user_2,
            organization.users.all(),
        )
