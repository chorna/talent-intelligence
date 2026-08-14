# apps/jobs/models/application.py

from django.db import models

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel
from apps.jobs.choices import ApplicationStatus

from .job import Job


class Application(BaseModel):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.NEW,
    )
    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application",
            ),
        ]

    def __str__(self):
        return f"{self.candidate} - {self.job}"
