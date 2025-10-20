from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include('users.urls')),  # Include users app URLs
    path('', include('sds_app.urls')),  # Include _app URLs
    path('ckeditor/', include('ckeditor_uploader.urls')),  # CKEditor URLS
     # path('accounts/', include('django.contrib.auth.urls')),  # Default auth URLs, commented out to let custom views take effect
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Allow media files in dev
