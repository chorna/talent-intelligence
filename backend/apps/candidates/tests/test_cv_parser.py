from unittest.mock import Mock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.candidates.exceptions import CVParsingError
from apps.candidates.services.cv_parser import CVParser


class CVParserTests(TestCase):
    def setUp(self):
        self.parser = CVParser()

    def test_parse_pdf(self):
        uploaded_file = SimpleUploadedFile(
            "cv.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        expected_text = "Christian Horna\nSenior Backend Engineer\nPython Django"

        with patch(
            "apps.candidates.services.cv_parser.PdfReader",
        ) as pdf_reader:
            page = Mock()
            page.extract_text.return_value = expected_text

            pdf_reader.return_value.pages = [page]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(result, expected_text)
        pdf_reader.assert_called_once()

    def test_parse_pdf_with_multiple_pages(self):
        uploaded_file = SimpleUploadedFile(
            "cv.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        with patch(
            "apps.candidates.services.cv_parser.PdfReader",
        ) as pdf_reader:
            page_1 = Mock()
            page_1.extract_text.return_value = "Page 1"

            page_2 = Mock()
            page_2.extract_text.return_value = "Page 2"

            pdf_reader.return_value.pages = [
                page_1,
                page_2,
            ]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(
            result,
            "Page 1\nPage 2",
        )

    def test_parse_docx(self):
        uploaded_file = SimpleUploadedFile(
            "cv.docx",
            b"fake docx content",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        with patch(
            "apps.candidates.services.cv_parser.Document",
        ) as document:
            paragraph_1 = Mock()
            paragraph_1.text = "Christian Horna"

            paragraph_2 = Mock()
            paragraph_2.text = "Senior Backend Engineer"

            document.return_value.paragraphs = [
                paragraph_1,
                paragraph_2,
            ]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(
            result,
            "Christian Horna\nSenior Backend Engineer",
        )

    def test_parse_docx_ignores_empty_paragraphs(self):
        uploaded_file = SimpleUploadedFile(
            "cv.docx",
            b"fake docx content",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        with patch(
            "apps.candidates.services.cv_parser.Document",
        ) as document:
            paragraph_1 = Mock()
            paragraph_1.text = "Christian Horna"

            paragraph_2 = Mock()
            paragraph_2.text = ""

            paragraph_3 = Mock()
            paragraph_3.text = "Python Developer"

            document.return_value.paragraphs = [
                paragraph_1,
                paragraph_2,
                paragraph_3,
            ]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(
            result,
            "Christian Horna\nPython Developer",
        )

    def test_parse_unsupported_file_type(self):
        uploaded_file = SimpleUploadedFile(
            "cv.txt",
            b"plain text",
            content_type="text/plain",
        )

        with self.assertRaisesMessage(
            CVParsingError,
            "Unsupported CV format: .txt",
        ):
            self.parser.parse(uploaded_file)

    def test_parse_empty_pdf(self):
        uploaded_file = SimpleUploadedFile(
            "cv.pdf",
            b"fake pdf content",
            content_type="application/pdf",
        )

        with patch(
            "apps.candidates.services.cv_parser.PdfReader",
        ) as pdf_reader:
            page = Mock()
            page.extract_text.return_value = None

            pdf_reader.return_value.pages = [page]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(result, "")

    def test_parse_empty_docx(self):
        uploaded_file = SimpleUploadedFile(
            "cv.docx",
            b"fake docx content",
            content_type=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
        )

        with patch(
            "apps.candidates.services.cv_parser.Document",
        ) as document:
            paragraph = Mock()
            paragraph.text = ""

            document.return_value.paragraphs = [
                paragraph,
            ]

            result = self.parser.parse(uploaded_file)

        self.assertEqual(result, "")
