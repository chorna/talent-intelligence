# Create your tests here.
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate


class CandidateViewSetTests(APITestCase):
    def setUp(self):
        self.url = "/api/candidates/"

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            phone="999999999",
            location="Lima, Peru",
            linkedin_url="https://linkedin.com/in/christian",
            github_url="https://github.com/christian",
        )

    def test_list_candidates(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["email"],
            self.candidate.email,
        )

    def test_retrieve_candidate(self):
        response = self.client.get(f"{self.url}{self.candidate.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["id"],
            str(self.candidate.id),
        )
        self.assertEqual(response.data["email"], self.candidate.email)

    def test_create_candidate(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "email": "juan@example.com",
            "phone": "988888888",
            "location": "Lima, Peru",
            "linkedin_url": "https://linkedin.com/in/juan",
            "github_url": "https://github.com/juan",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Candidate.objects.count(), 2)
        self.assertEqual(response.data["email"], data["email"])

    def test_update_candidate(self):
        data = {
            "first_name": "Christian Updated",
            "last_name": "Horna",
            "email": self.candidate.email,
            "phone": self.candidate.phone,
            "location": self.candidate.location,
            "linkedin_url": self.candidate.linkedin_url,
            "github_url": self.candidate.github_url,
        }

        response = self.client.put(
            f"{self.url}{self.candidate.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.first_name, "Christian Updated")

    def test_partial_update_candidate(self):
        data = {
            "location": "Chiclayo, Peru",
        }

        response = self.client.patch(
            f"{self.url}{self.candidate.id}/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.candidate.refresh_from_db()
        self.assertEqual(self.candidate.location, "Chiclayo, Peru")

    def test_delete_candidate(self):
        response = self.client.delete(f"{self.url}{self.candidate.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Candidate.objects.filter(id=self.candidate.id).exists())

    def test_create_candidate_with_duplicate_email(self):
        data = {
            "first_name": "Another",
            "last_name": "Candidate",
            "email": self.candidate.email,
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
        self.assertIn("email", response.data)

    def test_create_candidate_normalizes_email(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "email": "  JUAN@EXAMPLE.COM  ",
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
            response.data["email"],
            "juan@example.com",
        )
