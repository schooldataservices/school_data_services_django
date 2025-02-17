from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from users import views as user_views
from django.contrib.auth import views as auth_views
from emailscraper_app.views.homepage_views import serve_image
import debug_toolbar

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'), #class based views, built in
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'), #will not handle templates, must be implemented
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), 
         name='password_reset'), 
    path('password-reset/done', 
         auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), 
         name='password_reset_done'), 
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), 
         name='password_reset_confirm'), 
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), 
         name='password_reset_complete'), 
    path('', include('emailscraper_app.urls')),
    path('serve-image/', serve_image, name='serve_image'),

    path('ckeditor/', include('ckeditor_uploader.urls'))
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #allow our media to work in dev