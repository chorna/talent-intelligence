from django.db import models

# Create your models here.
from apps.core.models.base import BaseModel
from apps.locations.models.country import Country


class City(BaseModel):
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="cities",
    )
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["country__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["country", "name"],
                name="unique_city_per_country",
            ),
        ]

    def __str__(self):
        return f"{self.name}, {self.country.name}"
