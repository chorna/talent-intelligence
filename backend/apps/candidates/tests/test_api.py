# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.education.models import Education
from apps.experiences.models import Experience
from apps.skills.models import Skill


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

        self.python = Skill.objects.create(
            name="Python",
            slug="python",
        )

        self.django = Skill.objects.create(
            name="Django",
            slug="django",
        )

        self.candidate.skills.add(
            self.python,
            self.django,
        )

        self.experience = Experience.objects.create(
            candidate=self.candidate,
            company_name="Tech Company",
            job_title="Senior Backend Engineer",
            description="Developed APIs with Django.",
            location="Lima",
            employment_type="full_time",
            work_mode="hybrid",
            start_date="2024-01-01",
            end_date="2025-01-01",
            is_current=False,
        )

        self.education = Education.objects.create(
            candidate=self.candidate,
            institution="Universidad de Lima",
            degree="bachelor",
            field_of_study="Computer Science",
            location="Lima",
            start_date="2018-01-01",
            end_date="2023-12-31",
            is_current=False,
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

    def test_create_candidate_with_skills(self):
        data = {
            "first_name": "Another",
            "last_name": "Candidate",
            "email": "another@example.com",
            "skill_ids": [
                str(self.python.id),
                str(self.django.id),
            ],
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

        candidate = Candidate.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            candidate.skills.count(),
            2,
        )

        self.assertIn(
            self.python,
            candidate.skills.all(),
        )

        self.assertIn(
            self.django,
            candidate.skills.all(),
        )

    def test_retrieve_candidate_with_skills(self):
        self.candidate.skills.add(
            self.python,
            self.django,
        )

        response = self.client.get(
            reverse(
                "candidate-detail",
                kwargs={"pk": self.candidate.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        skill_ids = {skill["id"] for skill in response.data["skills"]}

        self.assertEqual(
            skill_ids,
            {
                str(self.python.id),
                str(self.django.id),
            },
        )

    def test_update_candidate_skills(self):
        self.candidate.skills.add(self.python)

        response = self.client.patch(
            reverse(
                "candidate-detail",
                kwargs={"pk": self.candidate.id},
            ),
            {
                "skill_ids": [str(self.django.id)],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.candidate.refresh_from_db()

        self.assertEqual(
            list(self.candidate.skills.all()),
            [self.django],
        )

    def test_retrieve_candidate_returns_skills(self):
        self.candidate.skills.add(self.python, self.django)

        response = self.client.get(
            reverse(
                "candidate-detail",
                kwargs={"pk": self.candidate.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data["skills"]), 2)

        skill_names = {skill["name"] for skill in response.data["skills"]}

        self.assertEqual(
            skill_names,
            {"Python", "Django"},
        )

    def test_retrieve_candidate_returns_experiences(self):
        response = self.client.get(
            reverse(
                "candidate-detail",
                kwargs={"pk": self.candidate.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["experiences"]),
            1,
        )

        experience = response.data["experiences"][0]

        self.assertEqual(
            experience["company_name"],
            self.experience.company_name,
        )

        self.assertEqual(
            experience["job_title"],
            self.experience.job_title,
        )

    def test_retrieve_candidate_returns_educations(self):
        response = self.client.get(
            reverse(
                "candidate-detail",
                kwargs={"pk": self.candidate.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["educations"]),
            1,
        )

        education = response.data["educations"][0]

        self.assertEqual(
            education["institution"],
            self.education.institution,
        )

        self.assertEqual(
            education["degree"],
            self.education.degree,
        )
