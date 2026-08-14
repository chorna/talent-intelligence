from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.candidates.models import Candidate
from apps.core.models.base import BaseModel
from apps.jobs.choices import ApplicationStatus
from apps.jobs.models.application_status_history import (
    ApplicationStatusHistory,
)
from apps.jobs.models.job import Job


class Application(BaseModel):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.APPLIED,
    )
    notes = models.TextField(
        blank=True,
    )

    ALLOWED_TRANSITIONS = {
        ApplicationStatus.APPLIED: frozenset(
            {
                ApplicationStatus.SCREENING,
                ApplicationStatus.REJECTED,
            }
        ),
        ApplicationStatus.SCREENING: frozenset(
            {
                ApplicationStatus.INTERVIEW,
                ApplicationStatus.REJECTED,
            }
        ),
        ApplicationStatus.INTERVIEW: frozenset(
            {
                ApplicationStatus.OFFER,
                ApplicationStatus.REJECTED,
            }
        ),
        ApplicationStatus.OFFER: frozenset(
            {
                ApplicationStatus.HIRED,
                ApplicationStatus.REJECTED,
            }
        ),
        ApplicationStatus.HIRED: frozenset(),
        ApplicationStatus.REJECTED: frozenset(),
    }

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["candidate", "job"],
                name="unique_candidate_job_application",
            ),
        ]

    def __str__(self):
        return f"{self.candidate} - {self.job}"

    def can_transition_to(self, new_status):
        return new_status in self.ALLOWED_TRANSITIONS.get(
            self.status,
            set(),
        )

    @transaction.atomic
    def transition_to(self, new_status, changed_by):
        if not self.can_transition_to(new_status):
            raise ValidationError(
                {
                    "status": (
                        f"Cannot move application from "
                        f"'{self.status}' to "
                        f"'{new_status}'."
                    ),
                }
            )

        previous_status = self.status

        self.status = new_status
        self.save(
            update_fields=[
                "status",
                "updated_at",
            ],
        )

        ApplicationStatusHistory.objects.create(
            application=self,
            from_status=previous_status,
            to_status=new_status,
            changed_by=changed_by,
        )

    @classmethod
    @transaction.atomic
    def create_with_history(
        cls,
        *,
        candidate,
        job,
        changed_by,
        status=ApplicationStatus.APPLIED,
        notes="",
    ):
        application = cls.objects.create(
            candidate=candidate,
            job=job,
            status=status,
            notes=notes,
        )

        ApplicationStatusHistory.objects.create(
            application=application,
            from_status=None,
            to_status=application.status,
            changed_by=changed_by,
        )

        return application
