from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.candidates.choices import CandidateImportStatus
from apps.candidates.models import CandidateImport
from apps.candidates.services.candidate_import import CandidateImportProcessor
from apps.candidates.tests.base import CandidatesTestMixin


class CandidateImportProcessorTests(CandidatesTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.candidate_import = CandidateImport.objects.create(
            file=SimpleUploadedFile(
                "christian-horna.pdf",
                b"fake pdf content",
                content_type="application/pdf",
            ),
            original_filename="christian-horna.pdf",
            imported_by=self.recruiter,
        )

        self.processor = CandidateImportProcessor()

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    @patch(
        "apps.candidates.services.candidate_import.CandidateDataExtractor.extract",
    )
    def test_process_creates_candidate(
        self,
        mock_extract,
        mock_parse,
    ):
        mock_parse.return_value = """
        Christian Horna
        Senior Backend Engineer
        christian@example.com
        """

        mock_extract.return_value = {
            "first_name": "Imported",
            "last_name": "Candidate",
            "email": "imported@example.com",
            "phone": "999999999",
            "linkedin_url": "https://linkedin.com/in/imported",
            "github_url": "https://github.com/imported",
            "headline": "Senior Backend Engineer",
            "summary": "Python and Django backend engineer.",
        }

        candidate = self.processor.process(
            self.candidate_import,
        )

        self.assertIsNotNone(candidate)

        self.assertEqual(
            candidate.first_name,
            "Imported",
        )
        self.assertEqual(
            candidate.last_name,
            "Candidate",
        )
        self.assertEqual(
            candidate.email,
            "imported@example.com",
        )
        self.assertEqual(
            candidate.phone,
            "999999999",
        )
        self.assertEqual(
            candidate.linkedin_url,
            "https://linkedin.com/in/imported",
        )
        self.assertEqual(
            candidate.github_url,
            "https://github.com/imported",
        )
        self.assertEqual(
            candidate.headline,
            "Senior Backend Engineer",
        )
        self.assertEqual(
            candidate.summary,
            "Python and Django backend engineer.",
        )

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    @patch(
        "apps.candidates.services.candidate_import.CandidateDataExtractor.extract",
    )
    def test_process_links_candidate_to_import(
        self,
        mock_extract,
        mock_parse,
    ):
        mock_parse.return_value = "CV content"

        mock_extract.return_value = {
            "first_name": "Imported",
            "last_name": "Candidate",
            "email": "imported@example.com",
            "phone": "999999999",
            "linkedin_url": "https://linkedin.com/in/imported",
            "github_url": "https://github.com/imported",
            "headline": "Senior Backend Engineer",
            "summary": "Python and Django backend engineer.",
        }

        candidate = self.processor.process(
            self.candidate_import,
        )

        self.candidate_import.refresh_from_db()

        self.assertEqual(
            self.candidate_import.candidate,
            candidate,
        )

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    @patch(
        "apps.candidates.services.candidate_import.CandidateDataExtractor.extract",
    )
    def test_process_marks_import_as_completed(
        self,
        mock_extract,
        mock_parse,
    ):
        mock_parse.return_value = "CV content"

        mock_extract.return_value = {
            "first_name": "Imported",
            "last_name": "Candidate",
            "email": "imported@example.com",
            "phone": "999999999",
            "linkedin_url": "https://linkedin.com/in/imported",
            "github_url": "https://github.com/imported",
            "headline": "Senior Backend Engineer",
            "summary": "Python and Django backend engineer.",
        }

        self.processor.process(
            self.candidate_import,
        )

        self.candidate_import.refresh_from_db()

        self.assertEqual(
            self.candidate_import.status,
            CandidateImportStatus.COMPLETED,
        )

        self.assertEqual(
            self.candidate_import.error_message,
            "",
        )

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    def test_process_marks_import_as_failed_when_parser_fails(
        self,
        mock_parse,
    ):
        mock_parse.side_effect = ValueError(
            "Unable to parse CV file.",
        )

        with self.assertRaises(ValueError):
            self.processor.process(
                self.candidate_import,
            )

        self.candidate_import.refresh_from_db()

        self.assertEqual(
            self.candidate_import.status,
            CandidateImportStatus.FAILED,
        )

        self.assertEqual(
            self.candidate_import.error_message,
            "Unable to parse CV file.",
        )

        self.assertIsNone(
            self.candidate_import.candidate,
        )

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    def test_parser_is_called_with_import_file(
        self,
        mock_parse,
    ):
        mock_parse.return_value = "CV content"

        with patch(
            "apps.candidates.services.candidate_import.CandidateDataExtractor.extract",
        ) as mock_extract:
            mock_extract.return_value = {
                "first_name": "Imported",
                "last_name": "Candidate",
                "email": "imported@example.com",
                "phone": "999999999",
                "linkedin_url": "https://linkedin.com/in/imported",
                "github_url": "https://github.com/imported",
                "headline": "Senior Backend Engineer",
                "summary": "Python and Django backend engineer.",
            }

            self.processor.process(
                self.candidate_import,
            )

        mock_parse.assert_called_once_with(
            self.candidate_import.file,
        )

    @patch(
        "apps.candidates.services.candidate_import.CVParser.parse",
    )
    def test_extractor_is_called_with_parsed_text(
        self,
        mock_parse,
    ):
        mock_parse.return_value = "Parsed CV text"

        with patch(
            "apps.candidates.services.candidate_import.CandidateDataExtractor.extract",
        ) as mock_extract:
            mock_extract.return_value = {
                "first_name": "Imported",
                "last_name": "Candidate",
                "email": "imported@example.com",
                "phone": "999999999",
                "linkedin_url": "https://linkedin.com/in/imported",
                "github_url": "https://github.com/imported",
                "headline": "Senior Backend Engineer",
                "summary": "Python and Django backend engineer.",
            }

            self.processor.process(
                self.candidate_import,
            )

        mock_extract.assert_called_once_with(
            "Parsed CV text",
        )
