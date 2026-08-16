from django.db import models

from apps.clients.models.client import Client
from apps.core.models.base import BaseModel


class ClientContact(BaseModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="contacts",
    )
    name = models.CharField(
        max_length=150,
    )
    email = models.EmailField()
    phone = models.CharField(
        max_length=30,
        blank=True,
    )
    position = models.CharField(
        max_length=100,
        blank=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.client.name}"
