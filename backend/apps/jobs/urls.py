from django.urls import include, path

urlpatterns = [
    path(
        "",
        include("apps.jobs.api.urls"),
    ),
]
