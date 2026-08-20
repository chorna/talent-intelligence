from django.test import TestCase

from apps.candidates.choices import CandidateImportStatus
from apps.candidates.models import CandidateImport
from apps.candidates.tests.base import CandidatesTestMixin


class CandidateImportModelTests(CandidatesTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.imported_by = self.recruiter

    def create_import(self, **kwargs):
        defaults = {
            "file": "candidate-imports/cv.pdf",
            "original_filename": "cv.pdf",
            "imported_by": self.imported_by,
        }
        defaults.update(kwargs)

        return CandidateImport.objects.create(**defaults)

    def test_create_candidate_import(self):
        candidate_import = self.create_import()

        self.assertIsNotNone(candidate_import.id)
        self.assertEqual(
            candidate_import.original_filename,
            "cv.pdf",
        )
        self.assertEqual(
            candidate_import.imported_by,
            self.imported_by,
        )

    def test_default_status_is_pending(self):
        candidate_import = self.create_import()

        self.assertEqual(
            candidate_import.status,
            CandidateImportStatus.PENDING,
        )

    def test_error_message_is_optional(self):
        candidate_import = self.create_import()

        self.assertEqual(
            candidate_import.error_message,
            "",
        )

    def test_candidate_is_optional(self):
        candidate_import = self.create_import()

        self.assertIsNone(
            candidate_import.candidate,
        )

    def test_string_representation(self):
        candidate_import = self.create_import(
            original_filename="christian-horna-cv.pdf",
        )

        self.assertEqual(
            str(candidate_import),
            "christian-horna-cv.pdf",
        )

    def test_import_can_be_linked_to_candidate(self):
        candidate_import = self.create_import(
            candidate=self.candidate,
        )

        self.assertEqual(
            candidate_import.candidate,
            self.candidate,
        )

    def test_import_is_deleted_when_imported_by_user_is_deleted(self):
        """
        This test is intentionally omitted because imported_by
        uses PROTECT. The import history must survive user-related
        deletion attempts.
        """
        pass
