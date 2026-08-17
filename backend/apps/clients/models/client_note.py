from django.db import models

from apps.clients.models.client import Client
from apps.core.models.base import BaseModel
from apps.users.models import User


class ClientNote(BaseModel):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="client_notes",
    )
    content = models.TextField()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.client.name}"
