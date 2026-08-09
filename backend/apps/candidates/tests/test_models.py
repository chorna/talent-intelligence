from django.db import IntegrityError
from django.test import TestCase

from apps.candidates.models import Candidate, CandidateFavorite, CandidateNote
from apps.users.models import User


class CandidateFavoriteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
        )

    def test_create_favorite(self):
        favorite = CandidateFavorite.objects.create(
            user=self.user,
            candidate=self.candidate,
        )

        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.candidate, self.candidate)

    def test_cannot_create_duplicate_favorite(self):
        CandidateFavorite.objects.create(
            user=self.user,
            candidate=self.candidate,
        )

        with self.assertRaises(IntegrityError):
            CandidateFavorite.objects.create(
                user=self.user,
                candidate=self.candidate,
            )

    def test_different_users_can_favorite_same_candidate(self):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="testpassword123",
        )

        CandidateFavorite.objects.create(
            user=self.user,
            candidate=self.candidate,
        )

        CandidateFavorite.objects.create(
            user=another_user,
            candidate=self.candidate,
        )

        self.assertEqual(
            CandidateFavorite.objects.filter(
                candidate=self.candidate,
            ).count(),
            2,
        )

    def test_str(self):
        favorite = CandidateFavorite.objects.create(
            user=self.user,
            candidate=self.candidate,
        )

        self.assertEqual(
            str(favorite),
            f"{self.user} → {self.candidate}",
        )


class CandidateNoteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

        self.candidate = Candidate.objects.create(
            first_name="Christian",
            last_name="Horna",
            email="christian@example.com",
        )

    def test_create_note(self):
        note = CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Buen nivel de Django y experiencia con AWS.",
        )

        self.assertEqual(note.user, self.user)
        self.assertEqual(note.candidate, self.candidate)
        self.assertEqual(
            note.content,
            "Buen nivel de Django y experiencia con AWS.",
        )

    def test_candidate_can_have_multiple_notes(self):
        CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Primera observación.",
        )

        CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Validar nivel de inglés.",
        )

        self.assertEqual(
            CandidateNote.objects.filter(
                user=self.user,
                candidate=self.candidate,
            ).count(),
            2,
        )

    def test_different_users_can_create_notes_for_same_candidate(self):
        another_user = User.objects.create_user(
            email="another@example.com",
            password="testpassword123",
        )

        CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Nota del recruiter 1.",
        )

        CandidateNote.objects.create(
            user=another_user,
            candidate=self.candidate,
            content="Nota del recruiter 2.",
        )

        self.assertEqual(
            CandidateNote.objects.filter(
                candidate=self.candidate,
            ).count(),
            2,
        )

    def test_str(self):
        note = CandidateNote.objects.create(
            user=self.user,
            candidate=self.candidate,
            content="Evaluar experiencia técnica.",
        )

        self.assertEqual(
            str(note),
            f"{self.user} → {self.candidate}",
        )
