from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.jobs.choices import InterviewStatus
from apps.jobs.models.interview import Interview

from .base import JobsTestMixin


class InterviewModelTests(JobsTestMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.submission = self.create_submission()

    def test_create_interview(self):
        scheduled_at = timezone.now() + timedelta(days=1)

        interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=scheduled_at,
            interviewer="John Doe",
            notes="Technical interview.",
        )

        self.assertIsNotNone(interview.pk)
        self.assertEqual(interview.submission, self.submission)
        self.assertEqual(interview.scheduled_at, scheduled_at)
        self.assertEqual(interview.status, InterviewStatus.SCHEDULED)
        self.assertEqual(interview.interviewer, "John Doe")
        self.assertEqual(interview.notes, "Technical interview.")

    def test_default_status_is_scheduled(self):
        interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=timezone.now(),
        )

        self.assertEqual(
            interview.status,
            InterviewStatus.SCHEDULED,
        )

    def test_interviewer_and_notes_are_optional(self):
        interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=timezone.now(),
        )

        self.assertEqual(interview.interviewer, "")
        self.assertEqual(interview.notes, "")

    def test_interview_is_deleted_when_submission_is_deleted(self):
        interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=timezone.now(),
        )

        interview_id = interview.id

        self.submission.delete()

        self.assertFalse(
            Interview.objects.filter(
                id=interview_id,
            ).exists(),
        )

    def test_submission_can_have_multiple_interviews(self):
        first_interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=timezone.now() + timedelta(days=1),
        )

        second_interview = Interview.objects.create(
            submission=self.submission,
            scheduled_at=timezone.now() + timedelta(days=2),
        )

        self.assertEqual(
            self.submission.interviews.count(),
            2,
        )

        self.assertIn(
            first_interview,
            self.submission.interviews.all(),
        )

        self.assertIn(
            second_interview,
            self.submission.interviews.all(),
        )
