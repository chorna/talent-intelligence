from django.db import models

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel
from apps.experiences.choices import EmploymentType, WorkMode
from apps.skills.models import Skill


class Experience(BaseModel):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="experiences",
    )
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(
        max_length=50,
        choices=EmploymentType.choices,
        blank=True,
    )
    work_mode = models.CharField(
        max_length=20,
        choices=WorkMode.choices,
        blank=True,
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
    )
    is_current = models.BooleanField(default=False)
    skills = models.ManyToManyField(
        Skill,
        related_name="experiences",
        blank=True,
    )

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
