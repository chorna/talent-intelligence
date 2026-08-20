from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.choices import InterviewStatus
from apps.jobs.models import CandidateSubmission


class Interview(BaseModel):
    submission = models.ForeignKey(
        CandidateSubmission,
        on_delete=models.CASCADE,
        related_name="interviews",
    )

    scheduled_at = models.DateTimeField()

    status = models.CharField(
        max_length=30,
        choices=InterviewStatus.choices,
        default=InterviewStatus.SCHEDULED,
    )

    interviewer = models.CharField(
        max_length=255,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )
