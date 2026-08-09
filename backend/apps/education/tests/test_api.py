from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.education.models import Education


@pytest.mark.django_db
class EducationViewSetTests(APITestCase):
    def setUp(self):
        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
        )

        self.education = Education.objects.create(
            candidate=self.candidate,
            institution="Universidad Nacional",
            degree="bachelor",
            field_of_study="Computer Science",
            location="Lima",
            start_date=date(2015, 1, 1),
            end_date=date(2020, 12, 31),
        )

        self.url = reverse("education-list")

    def test_list_educations(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_retrieve_education(self):
        response = self.client.get(
            reverse(
                "education-detail",
                kwargs={"pk": self.education.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            str(self.education.id),
        )

    def test_create_education(self):
        data = {
            "candidate": str(self.candidate.id),
            "institution": "Universidad de Lima",
            "degree": "bachelor",
            "field_of_study": "Computer Science",
            "location": "Lima",
            "start_date": "2018-01-01",
            "end_date": "2023-12-31",
            "is_current": False,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["institution"],
            "Universidad de Lima",
        )

    def test_create_education_normalizes_text_fields(self):
        data = {
            "candidate": str(self.candidate.id),
            "institution": "  Universidad    de   Lima  ",
            "degree": "  bachelor   Degree ",
            "field_of_study": "  Computer    Science ",
            "location": "  Lima    Peru ",
            "start_date": "2018-01-01",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            response.data["institution"],
            "Universidad de Lima",
        )
        self.assertEqual(
            response.data["degree"],
            "bachelor",
        )
        self.assertEqual(
            response.data["field_of_study"],
            "Computer Science",
        )
        self.assertEqual(
            response.data["location"],
            "Lima Peru",
        )

    def test_create_education_with_end_date_before_start_date(self):
        data = {
            "candidate": str(self.candidate.id),
            "institution": "University",
            "degree": "bachelor",
            "start_date": "2025-01-01",
            "end_date": "2024-01-01",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("end_date", response.data)

    def test_create_current_education_with_end_date(self):
        data = {
            "candidate": str(self.candidate.id),
            "institution": "University",
            "degree": "master",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "is_current": True,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("end_date", response.data)

    def test_create_current_education_without_end_date(self):
        data = {
            "candidate": str(self.candidate.id),
            "institution": "University",
            "degree": "master",
            "field_of_study": "Artificial Intelligence",
            "start_date": "2024-01-01",
            "is_current": True,
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(response.data["is_current"])
        self.assertIsNone(response.data["end_date"])

    def test_update_education(self):
        response = self.client.patch(
            reverse(
                "education-detail",
                kwargs={"pk": self.education.id},
            ),
            {
                "degree": "master",
                "field_of_study": "Software Engineering",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["degree"],
            "master",
        )
        self.assertEqual(
            response.data["field_of_study"],
            "Software Engineering",
        )

    def test_delete_education(self):
        response = self.client.delete(
            reverse(
                "education-detail",
                kwargs={"pk": self.education.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Education.objects.filter(
                id=self.education.id,
            ).exists()
        )

    def test_education_belongs_to_candidate(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            str(response.data[0]["candidate"]),
            str(self.candidate.id),
        )
