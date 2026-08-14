from django.urls import include, path

urlpatterns = [
    path(
        "",
        include("apps.organizations.api.urls"),
    ),
]
