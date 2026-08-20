from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from apps.candidates.models import CandidateImport
from apps.candidates.tests.base import CandidatesTestMixin


class CandidateImportViewSetTests(CandidatesTestMixin, APITestCase):
    def setUp(self):
        super().setUp()

        self.url = "/api/candidate-imports/"

        self.client.force_authenticate(
            user=self.recruiter,
        )

    def create_file(
        self,
        name="cv.pdf",
        content=b"fake pdf content",
    ):
        return SimpleUploadedFile(
            name,
            content,
            content_type="application/pdf",
        )

    def create_import(self, **kwargs):
        defaults = {
            "file": "candidate-imports/cv.pdf",
            "original_filename": "cv.pdf",
            "imported_by": self.recruiter,
        }
        defaults.update(kwargs)

        return CandidateImport.objects.create(
            **defaults,
        )

    def test_list_candidate_imports(self):
        self.create_import()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data),
            1,
        )

    def test_list_candidate_imports_returns_empty_list(self):
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data,
            [],
        )

    def test_create_candidate_import(self):
        response = self.client.post(
            self.url,
            {
                "file": self.create_file(
                    "christian-horna-cv.pdf",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        candidate_import = CandidateImport.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            candidate_import.original_filename,
            "christian-horna-cv.pdf",
        )

        self.assertEqual(
            candidate_import.imported_by,
            self.recruiter,
        )

    def test_create_candidate_import_defaults_to_pending(self):
        response = self.client.post(
            self.url,
            {
                "file": self.create_file(),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        candidate_import = CandidateImport.objects.get(
            id=response.data["id"],
        )

        self.assertEqual(
            candidate_import.status,
            "pending",
        )

    def test_create_rejects_unsupported_file_type(self):
        response = self.client.post(
            self.url,
            {
                "file": self.create_file(
                    "cv.txt",
                ),
            },
            format="multipart",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_retrieve_candidate_import(self):
        candidate_import = self.create_import()

        response = self.client.get(
            f"{self.url}{candidate_import.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(candidate_import.id),
        )

    def test_delete_candidate_import(self):
        candidate_import = self.create_import()

        response = self.client.delete(
            f"{self.url}{candidate_import.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            CandidateImport.objects.filter(
                id=candidate_import.id,
            ).exists(),
        )
