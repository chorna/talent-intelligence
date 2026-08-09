from django.urls import include, path

urlpatterns = [
    path("", include("apps.education.api.urls")),
]
