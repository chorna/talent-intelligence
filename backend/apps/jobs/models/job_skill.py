from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.models.job import Job
from apps.skills.models import Skill


class JobSkill(BaseModel):
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="job_skills",
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name="job_skills",
    )
    is_required = models.BooleanField(
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "skill"],
                name="unique_job_skill",
            ),
        ]
        indexes = [
            models.Index(
                fields=["skill", "job"],
                name="job_skill_skill_job_idx",
            ),
        ]

    def __str__(self):
        return f"{self.job} - {self.skill}"
