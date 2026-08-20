from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.jobs.choices import InterviewStatus
from apps.jobs.models.interview import Interview

from .base import JobsTestMixin


class InterviewViewSetTests(JobsTestMixin, APITestCase):
    def setUp(self):
        super().setUp()

        self.client.force_authenticate(
            user=self.recruiter,
        )

        self.submission = self.create_submission()

        self.interviewer = "John Doe"

        self.url = (
            f"/api/jobs/{self.job.id}/submissions/{self.submission.id}/interviews/"
        )

    def create_interview(self, **kwargs):
        defaults = {
            "submission": self.submission,
            "interviewer": self.interviewer,
            "scheduled_at": timezone.now() + timedelta(days=1),
            "status": InterviewStatus.SCHEDULED,
            "notes": "",
        }

        defaults.update(kwargs)

        return Interview.objects.create(**defaults)

    def test_list_interviews(self):
        interview = self.create_interview()

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

        self.assertEqual(
            str(response.data[0]["id"]),
            str(interview.id),
        )

    def test_list_interviews_returns_empty_list(self):
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

    def test_create_interview(self):
        scheduled_at = timezone.now() + timedelta(days=2)

        response = self.client.post(
            self.url,
            {
                "submission": str(self.submission.id),
                "interviewer": str(self.interviewer),
                "scheduled_at": scheduled_at.isoformat(),
                "status": InterviewStatus.SCHEDULED,
                "notes": "Technical interview.",
                "feedback": "",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        interview = Interview.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            interview.submission,
            self.submission,
        )

        self.assertEqual(
            interview.interviewer,
            self.interviewer,
        )

    def test_retrieve_interview(self):
        interview = self.create_interview()

        response = self.client.get(
            f"{self.url}{interview.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            str(response.data["id"]),
            str(interview.id),
        )

    def test_update_interview(self):
        interview = self.create_interview()

        response = self.client.patch(
            f"{self.url}{interview.id}/",
            {
                "status": InterviewStatus.COMPLETED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        interview.refresh_from_db()

        self.assertEqual(
            interview.status,
            InterviewStatus.COMPLETED,
        )

    def test_delete_interview(self):
        interview = self.create_interview()

        response = self.client.delete(
            f"{self.url}{interview.id}/",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Interview.objects.filter(
                pk=interview.id,
            ).exists(),
        )

    def test_create_interview_requires_interviewer(self):
        response = self.client.post(
            self.url,
            {
                "submission": str(self.submission.id),
                "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": InterviewStatus.SCHEDULED,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "interviewer",
            response.data,
        )

    def test_create_interview_rejects_invalid_status(self):
        response = self.client.post(
            self.url,
            {
                "submission": str(self.submission.id),
                "interviewer": str(self.interviewer),
                "scheduled_at": (timezone.now() + timedelta(days=1)).isoformat(),
                "status": "invalid_status",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "status",
            response.data,
        )
