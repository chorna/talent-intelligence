# Create your models here.
from django.db import models
from django.db.models.functions import Lower

from apps.core.models.base import BaseModel


class Skill(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="skill_name_ci_unique",
            ),
        ]

    def __str__(self):
        return self.name
