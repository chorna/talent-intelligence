# Create your tests here.
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate
from apps.education.models import Education
from apps.experiences.models import Experience
from apps.locations.models import City, Country
from apps.skills.models import Skill
from apps.users.models import User


class CandidateViewSetTests(APITestCase):
    def setUp(self):
        self.url = "/api/candidates/"

        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

        self.client.force_authenticate(user=self.user)

        # Countries
        self.peru = Country.objects.create(
            name="Peru",
            code="PE",
        )

        self.colombia = Country.objects.create(
            name="Colombia",
            code="CO",
        )

        # Cities
        self.lima = City.objects.create(
            country=self.peru,
            name="Lima",
        )

        self.chiclayo = City.objects.create(
            country=self.peru,
            name="Chiclayo",
        )

        self.bogota = City.objects.create(
            country=self.colombia,
            name="Bogota",
        )

        self.city = self.lima

        # Skills
        self.python = Skill.objects.create(
            name="Python",
            slug="python",
        )

        self.django = Skill.objects.create(
            name="Django",
            slug="django",
        )

        self.java = Skill.objects.create(
            name="Java",
            slug="java",
        )

        self.aws = Skill.objects.create(
            name="AWS",
            slug="aws",
        )

        # Candidate 1
        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
            phone="999999999",
            city=self.lima,
            headline="Senior Backend Engineer",
            summary="Python and Django backend engineer.",
            linkedin_url="https://linkedin.com/in/christian",
            github_url="https://github.com/christian",
        )

        self.candidate.skills.add(
            self.python,
            self.django,
        )

        # Candidate 2
        self.candidate_chiclayo = Candidate.objects.create(
            first_name="Juan",
            last_name="Perez",
            email="juan@example.com",
            phone="988888888",
            city=self.chiclayo,
            headline="Backend Developer",
            summary="Python developer.",
        )

        self.candidate_chiclayo.skills.add(
            self.python,
        )

        # Candidate 3
        self.candidate_colombia = Candidate.objects.create(
            first_name="Carlos",
            last_name="Gomez",
            email="carlos@example.com",
            phone="977777777",
            city=self.bogota,
            headline="Java Backend Developer",
            summary="Java backend developer.",
        )

        self.candidate_colombia.skills.add(
            self.java,
        )

        # Candidate 4
        self.candidate_full_stack = Candidate.objects.create(
            first_name="Pedro",
            last_name="Ramirez",
            email="pedro@example.com",
            phone="966666666",
            city=self.lima,
            headline="Senior Cloud Backend Engineer",
            summary="Python Django AWS backend engineer.",
        )

        self.candidate_full_stack.skills.add(
            self.python,
            self.django,
            self.aws,
        )

        # Experience for candidate 1
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

        # Education for candidate 1
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

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            4,
        )

        self.assertEqual(
            len(response.data["results"]),
            4,
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
            "first_name": "Pedro",
            "last_name": "Garcia",
            "email": "pedro.garcia@example.com",
            "phone": "988888888",
            "city": str(self.chiclayo.id),
            "linkedin_url": "https://linkedin.com/in/pedro",
            "github_url": "https://github.com/pedro",
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
            Candidate.objects.count(),
            5,
        )

        self.assertEqual(
            response.data["email"],
            "pedro.garcia@example.com",
        )

    def test_update_candidate(self):
        data = {
            "first_name": "Christian Updated",
            "last_name": "Horna",
            "email": self.candidate.email,
            "phone": self.candidate.phone,
            "city": str(self.candidate.city.id),
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
            "city": str(self.chiclayo.id),
        }

        response = self.client.patch(
            f"{self.url}{self.candidate.id}/",
            data,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.candidate.refresh_from_db()

        self.assertEqual(
            self.candidate.city,
            self.chiclayo,
        )

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
            "first_name": "Pedro",
            "last_name": "Garcia",
            "email": "  PEDRO2@EXAMPLE.COM  ",
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
            "pedro2@example.com",
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

    def test_retrieve_candidate_returns_city(self):
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
            str(response.data["city"]),
            str(self.city.id),
        )

    def test_create_candidate_with_invalid_city(self):
        data = {
            "first_name": "Juan",
            "last_name": "Perez",
            "email": "juan@example.com",
            "city": "00000000-0000-0000-0000-000000000000",
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
            "city",
            response.data,
        )

    def test_filter_candidates_by_skill(self):
        response = self.client.get(
            f"{self.url}?skill=python",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            3,
        )

        emails = {candidate["email"] for candidate in response.data["results"]}

        self.assertEqual(
            emails,
            {
                "christian@example.com",
                "juan@example.com",
                "pedro@example.com",
            },
        )

    def test_filter_candidates_by_city(self):
        response = self.client.get(
            f"{self.url}?city=lima",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        emails = {candidate["email"] for candidate in response.data["results"]}

        self.assertEqual(
            emails,
            {
                "christian@example.com",
                "pedro@example.com",
            },
        )

    def test_filter_candidates_by_country(self):
        response = self.client.get(
            f"{self.url}?country=PE",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            3,
        )

    def test_filter_candidates_by_skill_and_city(self):
        response = self.client.get(
            f"{self.url}?skill=python&city=lima",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

        emails = {candidate["email"] for candidate in response.data["results"]}

        self.assertEqual(
            emails,
            {
                "christian@example.com",
                "pedro@example.com",
            },
        )

    def test_search_candidates(self):
        response = self.client.get(
            f"{self.url}?search=christian",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )

        self.assertEqual(
            response.data["results"][0]["id"],
            str(self.candidate.id),
        )

    def test_candidates_are_paginated(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("count", response.data)
        self.assertIn("results", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        self.assertEqual(
            response.data["count"],
            4,
        )

    def test_candidates_page_size(self):
        response = self.client.get(
            f"{self.url}?page_size=2",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            2,
        )

        self.assertEqual(
            response.data["count"],
            4,
        )

    def test_order_candidates_by_first_name(self):
        response = self.client.get(
            f"{self.url}?ordering=first_name",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        names = [candidate["first_name"] for candidate in response.data["results"]]

        self.assertEqual(
            names,
            sorted(names),
        )

    def test_order_candidates_by_created_at_descending(self):
        response = self.client.get(
            f"{self.url}?ordering=-created_at",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        dates = [candidate["created_at"] for candidate in response.data["results"]]

        self.assertEqual(
            dates,
            sorted(dates, reverse=True),
        )

    def test_filter_candidates_by_multiple_skills(self):
        response = self.client.get(
            f"{self.url}?skills=python,django",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            2,
        )

    def test_filter_candidates_by_multiple_skills_requires_all_skills(self):
        response = self.client.get(
            f"{self.url}?skills=python,django,aws",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["count"],
            1,
        )
