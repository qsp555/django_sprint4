from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from blog.views import register

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/logout/', LogoutView.as_view(
        template_name='registration/logged_out.html',
        http_method_names=['get', 'post'],
    ), name='logout'),
    path('auth/registration/', register, name='registration'),
    path('auth/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'