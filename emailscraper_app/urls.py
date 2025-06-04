from django.urls import path
from .views import homepage_views, request_page_view, uploading_file_views
from emailscraper_app.static_sitemaps import StaticViewSitemap
from django.views.generic import TemplateView


sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [

    path('serve-file/<path:file_path>/', uploading_file_views.serve_gcs_file, name='serve_file'),
    path('update-completion-status/<int:config_id>/', request_page_view.update_completion_status, name='update_completion_status'),
    path('update-email-content/<int:request_id>/', request_page_view.update_email_content, name='update_email_content'),
    path('delete-request/<int:config_id>/', request_page_view.delete_request, name='delete_request'),
    path('', homepage_views.landing_page, name='landing_page'),
    path('challenges-faced/', homepage_views.problem_solution, name='challenges_faced'),
    path('data-modeling/', homepage_views.data_modeling, name='data_modeling'),
    path('data-pipelines/', homepage_views.data_pipelines, name='data_pipelines'),
    path('cloud-setup/', homepage_views.cloud_setup, name='cloud_setup'),
    #  path('pricing/', homepage_views.pricing_faqs, name='pricing'),

    path('filter-requests/', request_page_view.filter_requests, name='filter_requests'),
    path('submit-requests/', request_page_view.create_request_config, name='submit-requests'),
    path('api/notifications/', homepage_views.get_notifications, name='get_notifications'),
    path('api/notifications/mark-read/', homepage_views.mark_notifications_as_read, name='mark_notifications_as_read'),
    path('historical-requests/', request_page_view.historical_requests, name='historical_requests'),
    path('get-next-request-id/', request_page_view.get_next_request_id, name='get_next_request_id'),
    path('robots.txt', TemplateView.as_view(template_name="emailscraper_app/robots.txt", content_type="text/plain")),
]