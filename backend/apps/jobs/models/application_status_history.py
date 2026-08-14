from django.db import models

from apps.core.models.base import BaseModel
from apps.jobs.choices import ApplicationStatus
from apps.users.models import User


class ApplicationStatusHistory(BaseModel):
    application = models.ForeignKey(
        "jobs.Application",
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    from_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        null=True,
        blank=True,
    )
    to_status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="application_status_changes",
    )

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.application} {self.from_status} → {self.to_status}"
