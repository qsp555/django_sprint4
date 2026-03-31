"""URL config for the project."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from blog import views as blog_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/img/fav/favicon.ico", permanent=True),
    ),
    path("auth/registration/", blog_views.registration, name="registration"),
    path("auth/", include("django.contrib.auth.urls")),
    path("", include("pages.urls", namespace="pages")),
    path("", include("blog.urls", namespace="blog")),
]

handler404 = "pages.views.page_not_found"
handler500 = "pages.views.server_error"
