from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import Candidate, CandidateNote
from apps.users.models import User


class CandidateNoteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="recruiter@example.com",
            password="testpassword123",
        )

        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="testpassword123",
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
        )

        self.client.force_authenticate(
            user=self.user,
        )

        self.url = f"/api/candidates/{self.candidate.id}/notes/"

    def test_list_notes(self):
        CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Buen candidato.",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_create_note(self):
        response = self.client.post(
            self.url,
            {
                "content": "Validar experiencia con AWS.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        note = CandidateNote.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            note.user,
            self.user,
        )

        self.assertEqual(
            note.candidate,
            self.candidate,
        )

        self.assertEqual(
            note.content,
            "Validar experiencia con AWS.",
        )

    def test_user_cannot_see_other_users_notes(self):
        CandidateNote.objects.create(
            user=self.other_user,
            candidate=self.candidate,
            content="Nota privada de otro recruiter.",
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            0,
        )

    def test_user_cannot_update_other_users_note(self):
        note = CandidateNote.objects.create(
            user=self.other_user,
            candidate=self.candidate,
            content="Nota privada.",
        )

        response = self.client.patch(
            f"{self.url}{note.id}/",
            {
                "content": "Intento de modificar nota.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_delete_other_users_note(self):
        note = CandidateNote.objects.create(
            user=self.other_user,
            candidate=self.candidate,
            content="Nota privada.",
        )

        response = self.client.delete(
            f"{self.url}{note.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_update_own_note(self):
        note = CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Nota inicial.",
        )

        response = self.client.patch(
            f"{self.url}{note.id}/",
            {
                "content": "Nota actualizada.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        note.refresh_from_db()

        self.assertEqual(
            note.content,
            "Nota actualizada.",
        )

    def test_delete_own_note(self):
        note = CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Eliminar esta nota.",
        )

        response = self.client.delete(
            f"{self.url}{note.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            CandidateNote.objects.filter(
                id=note.id,
            ).exists()
        )
