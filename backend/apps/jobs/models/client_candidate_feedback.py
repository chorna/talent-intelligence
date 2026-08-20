from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.choices import ClientFeedbackDecision
from apps.jobs.models.candidate_submission import CandidateSubmission
from apps.users.models import User


class ClientCandidateFeedback(BaseModel):
    submission = models.ForeignKey(
        CandidateSubmission,
        on_delete=models.CASCADE,
        related_name="client_feedback",
    )
    decision = models.CharField(
        max_length=30,
        choices=ClientFeedbackDecision.choices,
    )
    comments = models.TextField(
        blank=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="client_candidate_feedback",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.submission.candidate} - {self.get_decision_display()}"
