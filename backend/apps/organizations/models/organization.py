# Create your models here.
from django.db import models

from apps.core.models.base import BaseModel


class Organization(BaseModel):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
