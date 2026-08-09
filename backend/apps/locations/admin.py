# Register your models here.
from django.contrib import admin

from apps.locations.models import City, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "is_active",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = ("is_active",)
    search_fields = (
        "name",
        "code",
    )
    ordering = ("name",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "country",
        "is_active",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = (
        "country",
        "is_active",
    )
    search_fields = (
        "name",
        "country__name",
        "country__code",
    )
    ordering = (
        "country__name",
        "name",
    )
