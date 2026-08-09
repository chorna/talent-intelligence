from django.urls import include, path

urlpatterns = [
    path("", include("apps.skills.api.urls")),
]
