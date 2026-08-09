from django.urls import include, path

urlpatterns = [
    path(
        "locations/",
        include("apps.locations.api.urls"),
    ),
]
