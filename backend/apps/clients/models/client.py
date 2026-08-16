# Create your models here.
from django.db import models

from apps.clients.choices import ClientStatus
from apps.core.models.base import BaseModel
from apps.organizations.models import Organization


class Client(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(
        max_length=150,
    )
    website = models.URLField(
        blank=True,
    )
    description = models.TextField(
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ClientStatus.choices,
        default=ClientStatus.ACTIVE,
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_client_name_per_organization",
            ),
        ]

    def __str__(self):
        return self.name
