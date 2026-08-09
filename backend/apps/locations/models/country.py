from django.db import models

# Create your models here.
from apps.core.models.base import BaseModel


class Country(BaseModel):
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    code = models.CharField(
        max_length=2,
        unique=True,
    )
    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
