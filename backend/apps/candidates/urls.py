from django.urls import include, path

urlpatterns = [
    path("", include("apps.candidates.api.urls")),
]
