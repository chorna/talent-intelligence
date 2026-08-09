from datetime import date

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.experiences.models import Experience
from apps.skills.models import Skill


class ExperienceViewSetTests(APITestCase):
    def setUp(self):
        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
        )

        self.python = Skill.objects.create(
            name="Python",
            slug="python",
        )

        self.django = Skill.objects.create(
            name="Django",
            slug="django",
        )

        self.experience = Experience.objects.create(
            candidate=self.candidate,
            company_name="Acme",
            job_title="Backend Developer",
            description="Developed backend services.",
            location="Lima",
            employment_type="full_time",
            work_mode="remote",
            start_date=date(2023, 1, 1),
            is_current=True,
        )

        self.experience.skills.add(
            self.python,
            self.django,
        )

        self.url = reverse("experience-list")

    def test_list_experiences(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(len(response.data), 1)

    def test_retrieve_experience(self):
        response = self.client.get(
            reverse(
                "experience-detail",
                kwargs={"pk": self.experience.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["id"],
            str(self.experience.id),
        )

    def test_create_experience(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Tech Company",
            "job_title": "Senior Backend Engineer",
            "description": "Developed APIs with Django.",
            "location": "Lima",
            "employment_type": "full_time",
            "work_mode": "hybrid",
            "start_date": "2024-01-01",
            "end_date": "2025-01-01",
            "is_current": False,
            "skills": [
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

        experience = Experience.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            experience.company_name,
            "Tech Company",
        )

        self.assertEqual(
            experience.skills.count(),
            2,
        )

    def test_update_experience(self):
        response = self.client.patch(
            reverse(
                "experience-detail",
                kwargs={"pk": self.experience.id},
            ),
            {
                "job_title": "Senior Backend Engineer",
                "work_mode": "hybrid",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.experience.refresh_from_db()

        self.assertEqual(
            self.experience.job_title,
            "Senior Backend Engineer",
        )

        self.assertEqual(
            self.experience.work_mode,
            "hybrid",
        )

    def test_delete_experience(self):
        response = self.client.delete(
            reverse(
                "experience-detail",
                kwargs={"pk": self.experience.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Experience.objects.filter(
                id=self.experience.id,
            ).exists()
        )

    def test_create_experience_with_invalid_employment_type(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Tech Company",
            "job_title": "Developer",
            "start_date": "2024-01-01",
            "employment_type": "invalid_type",
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

        self.assertIn(
            "employment_type",
            response.data,
        )

    def test_create_experience_with_invalid_work_mode(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Tech Company",
            "job_title": "Developer",
            "start_date": "2024-01-01",
            "work_mode": "invalid_mode",
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

        self.assertIn(
            "work_mode",
            response.data,
        )

    def test_create_experience_with_end_date_before_start_date(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Tech Company",
            "job_title": "Developer",
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

        self.assertIn(
            "end_date",
            response.data,
        )

    def test_create_current_experience_with_end_date(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Tech Company",
            "job_title": "Developer",
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

        self.assertIn(
            "end_date",
            response.data,
        )

    def test_create_experience_normalizes_text_fields(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "  Acme    Corporation  ",
            "job_title": "  Senior    Backend Engineer ",
            "location": "  Lima    Peru ",
            "start_date": "2024-01-01",
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

        experience = Experience.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            experience.company_name,
            "Acme Corporation",
        )

        self.assertEqual(
            experience.job_title,
            "Senior Backend Engineer",
        )

        self.assertEqual(
            experience.location,
            "Lima Peru",
        )

    def test_create_experience_with_skills(self):
        data = {
            "candidate": str(self.candidate.id),
            "company_name": "Another Company",
            "job_title": "Backend Developer",
            "start_date": "2024-01-01",
            "skills": [
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

        experience = Experience.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            experience.skills.count(),
            2,
        )

        self.assertIn(
            self.python,
            experience.skills.all(),
        )

        self.assertIn(
            self.django,
            experience.skills.all(),
        )

    def test_retrieve_experience_returns_skills(self):
        response = self.client.get(
            reverse(
                "experience-detail",
                kwargs={"pk": self.experience.id},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        skill_ids = {str(skill_id) for skill_id in response.data["skills"]}

        self.assertEqual(
            skill_ids,
            {
                str(self.python.id),
                str(self.django.id),
            },
        )
