from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.choices import Currency, OfferStatus
from apps.jobs.models.candidate_submission import CandidateSubmission


class Offer(BaseModel):
    submission = models.ForeignKey(
        CandidateSubmission,
        on_delete=models.CASCADE,
        related_name="offers",
    )

    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.PEN,
    )

    status = models.CharField(
        max_length=30,
        choices=OfferStatus.choices,
        default=OfferStatus.DRAFT,
    )

    offered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    responded_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.submission.candidate} - {self.salary} {self.currency}"
