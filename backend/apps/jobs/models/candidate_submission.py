from django.db import models

from apps.candidates.models import Candidate
from apps.clients.models import Client
from apps.core.models.base import BaseModel
from apps.jobs.choices import SubmissionStatus
from apps.jobs.models.job import Job
from apps.users.models import User


class CandidateSubmission(BaseModel):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="candidate_submissions",
    )
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="candidate_submissions",
    )
    status = models.CharField(
        max_length=30,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.PENDING,
    )
    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"],
                name="unique_candidate_submission_per_job",
            ),
        ]

    def __str__(self):
        return f"{self.candidate} - {self.job}"
