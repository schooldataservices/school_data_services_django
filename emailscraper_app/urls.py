from django.urls import path
from .views import homepage_views, CRM_views, request_page_view
from .views.uploading_file_views import (
    EmailListView, EmailDetailView, EmailCreateView,
    EmailUpdateView, EmailDeleteView, serve_gcs_file
)

urlpatterns = [
    path('email/', EmailListView.as_view(), name='email'),
    path('email/<int:pk>/', EmailDetailView.as_view(), name='email-detail'),
    path('import-file/', EmailCreateView.as_view(), name='import-file'),
    path('serve-file/<path:file_path>/', serve_gcs_file, name='serve_file'),
    path('email/<int:pk>/update/', EmailUpdateView.as_view(), name='email-update'),
    path('email/<int:pk>/delete/', EmailDeleteView.as_view(), name='email-delete'),
    path('', homepage_views.landing_page, name='landing_page'),
    path('submit-requests/', request_page_view.create_request_config, name='submit-requests'),
    path('send-emails/', homepage_views.send_emails_view, name='email_send'),
    path('file-uploads/', homepage_views.file_list, name='file_list'),
    path('temp/', homepage_views.email_content_view, name='temp'),
    path('create-customer/', CRM_views.customer_create_view, name='create-customer'),
    path('search-contacts/', CRM_views.search_contacts, name='search-contacts'),
    path('get-contact-details/', CRM_views.get_contact_details, name='get-contact-details'),
    path('update-completion-status/<int:config_id>/', request_page_view.update_completion_status, name='update_completion_status'),
    path('update-email-content/<int:config_id>/', request_page_view.update_email_content, name='update_email_content'),
    path('delete-request/<int:config_id>/', request_page_view.delete_request, name='delete_request'),
]