# Create your tests here.

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.skills.models import Skill


class SkillViewSetTests(APITestCase):
    def setUp(self):
        self.url = reverse("skill-list")

        self.skill = Skill.objects.create(
            name="Python",
            slug="python",
            description="Python programming language",
        )

    def test_list_skills(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Python")
        self.assertEqual(response.data[0]["slug"], "python")

    def test_retrieve_skill(self):
        response = self.client.get(
            reverse("skill-detail", kwargs={"pk": self.skill.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.skill.id))
        self.assertEqual(response.data["name"], "Python")
        self.assertEqual(response.data["slug"], "python")

    def test_create_skill_generates_slug(self):
        data = {
            "name": "Django REST Framework",
            "description": "Framework for building APIs with Django.",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Django REST Framework")
        self.assertEqual(response.data["slug"], "django-rest-framework")

    def test_create_skill_normalizes_name(self):
        data = {
            "name": "  Django    REST Framework  ",
        }

        response = self.client.post(
            self.url,
            data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["name"],
            "Django REST Framework",
        )
        self.assertEqual(
            response.data["slug"],
            "django-rest-framework",
        )

    def test_create_skill_with_duplicate_name(self):
        data = {
            "name": "Python",
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
        self.assertIn("name", response.data)

    def test_create_skill_with_case_insensitive_duplicate_name(self):
        data = {
            "name": "PYTHON",
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

    def test_update_skill_name_updates_slug(self):
        response = self.client.patch(
            reverse("skill-detail", kwargs={"pk": self.skill.id}),
            {
                "name": "Django REST Framework",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["name"],
            "Django REST Framework",
        )
        self.assertEqual(
            response.data["slug"],
            "django-rest-framework",
        )

    def test_delete_skill(self):
        response = self.client.delete(
            reverse("skill-detail", kwargs={"pk": self.skill.id})
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(Skill.objects.filter(id=self.skill.id).exists())
