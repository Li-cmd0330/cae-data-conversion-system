from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/materials/', include('apps.materials.urls')),
    path('api/conversion/', include('apps.conversion.urls')),
    path('api/validation/', include('apps.validation.urls')),
    path('api/algorithms/', include('apps.algorithms.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
