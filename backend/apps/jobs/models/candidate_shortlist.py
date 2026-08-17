from django.db import models

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel
from apps.jobs.models.job import Job
from apps.users.models import User


class CandidateShortlist(BaseModel):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="shortlist",
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="shortlists",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="candidate_shortlists",
    )
    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"],
                name="unique_candidate_shortlist_per_job",
            ),
        ]

    def __str__(self):
        return f"{self.candidate} - {self.job}"
