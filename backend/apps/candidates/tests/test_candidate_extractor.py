from django.test import SimpleTestCase

from apps.candidates.services.candidate_extractor import (
    CandidateDataExtractor,
)


class CandidateDataExtractorTests(SimpleTestCase):
    def setUp(self):
        self.extractor = CandidateDataExtractor()

        self.cv_text = """
        Christian Horna
        Senior Backend Engineer

        Email: christian.horna@example.com
        Phone: +51 999 999 999

        LinkedIn:
        https://linkedin.com/in/christian-horna

        GitHub:
        https://github.com/christian-horna

        Summary
        Backend engineer with 10+ years of experience
        building APIs with Python and Django.

        Experience
        Senior Backend Engineer
        Tech Company
        """

    def test_extracts_first_name(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(data["first_name"], "Christian")

    def test_extracts_last_name(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(data["last_name"], "Horna")

    def test_extracts_email(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["email"],
            "christian.horna@example.com",
        )

    def test_extracts_phone(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["phone"],
            "+51 999 999 999",
        )

    def test_extracts_linkedin_url(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["linkedin_url"],
            "https://linkedin.com/in/christian-horna",
        )

    def test_extracts_github_url(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["github_url"],
            "https://github.com/christian-horna",
        )

    def test_extracts_headline(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["headline"],
            "Senior Backend Engineer",
        )

    def test_extracts_summary(self):
        data = self.extractor.extract(self.cv_text)

        self.assertEqual(
            data["summary"],
            (
                "Backend engineer with 10+ years of experience "
                "building APIs with Python and Django."
            ),
        )

    def test_empty_text_returns_empty_result(self):
        data = self.extractor.extract("")

        self.assertEqual(
            data,
            {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "linkedin_url": "",
                "github_url": "",
                "headline": "",
                "summary": "",
            },
        )

    def test_none_text_returns_empty_result(self):
        data = self.extractor.extract(None)

        self.assertEqual(
            data,
            {
                "first_name": "",
                "last_name": "",
                "email": "",
                "phone": "",
                "linkedin_url": "",
                "github_url": "",
                "headline": "",
                "summary": "",
            },
        )

    def test_missing_optional_data(self):
        text = """
        Christian Horna
        Senior Backend Engineer
        """

        data = self.extractor.extract(text)

        self.assertEqual(data["first_name"], "Christian")
        self.assertEqual(data["last_name"], "Horna")
        self.assertEqual(data["headline"], "Senior Backend Engineer")
        self.assertEqual(data["email"], "")
        self.assertEqual(data["phone"], "")
        self.assertEqual(data["linkedin_url"], "")
        self.assertEqual(data["github_url"], "")
        self.assertEqual(data["summary"], "")
