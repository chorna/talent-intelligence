from django.conf import settings
from django.db import models

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel


class CandidateNote(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="candidate_notes",
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} → {self.candidate}"
