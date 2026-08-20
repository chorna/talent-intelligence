from django.conf import settings
from django.db import models

from apps.candidates.choices import CandidateImportStatus
from apps.core.models.base import BaseModel


class CandidateImport(BaseModel):
    file = models.FileField(
        upload_to="candidate-imports/%Y/%m/%d/",
    )
    original_filename = models.CharField(
        max_length=255,
    )
    status = models.CharField(
        max_length=30,
        choices=CandidateImportStatus.choices,
        default=CandidateImportStatus.PENDING,
    )
    error_message = models.TextField(
        blank=True,
    )
    candidate = models.ForeignKey(
        "candidates.Candidate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imports",
    )
    imported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="candidate_imports",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_filename
