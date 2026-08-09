from django.db import models

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel
from apps.education.choices import DegreeChoices


class Education(BaseModel):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="educations",
    )
    institution = models.CharField(max_length=255)
    degree = models.CharField(
        max_length=50,
        choices=DegreeChoices.choices,
        blank=True,
    )
    field_of_study = models.CharField(
        max_length=255,
        blank=True,
    )
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date", "-created_at"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"
