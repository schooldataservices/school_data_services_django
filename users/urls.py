from django.urls import path
from users import views as user_views
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', user_views.register, name='register'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', user_views.login_view, name='login'),  # Ensure this is the custom login view
    path('logout/', auth_views.LogoutView.as_view(next_page='landing_page'), name='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'), 
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'), 
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'), 
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'), 
    path('ckeditor/upload/', user_views.custom_ckeditor_upload, name='custom_ckeditor_upload'),  # Custom CKEditor upload view
    path('activate/<uidb64>/<token>/', views.activate, name='activate')
]
