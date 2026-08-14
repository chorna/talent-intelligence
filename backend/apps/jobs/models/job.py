# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.choices import EmploymentType, JobStatus, WorkMode
from apps.locations.models import City
from apps.organizations.models import Organization


class Job(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    city = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="jobs",
        null=True,
        blank=True,
    )
    employment_type = models.CharField(
        max_length=30,
        choices=EmploymentType.choices,
    )
    work_mode = models.CharField(
        max_length=30,
        choices=WorkMode.choices,
    )
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.DRAFT,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="jobs",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()

        if self.work_mode == WorkMode.REMOTE and self.city is not None:
            raise ValidationError(
                {
                    "city": "Remote jobs cannot have a city.",
                }
            )

        if (
            self.work_mode
            in {
                WorkMode.HYBRID,
                WorkMode.ON_SITE,
            }
            and self.city is None
        ):
            raise ValidationError(
                {
                    "city": "City is required for hybrid and on-site jobs.",
                }
            )
