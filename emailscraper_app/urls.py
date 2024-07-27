from django.urls import path
from .views import homepage_views
from .views.uploading_file_views import (EmailListView,
                                        EmailDetailView, 
                                        EmailCreateView,
                                        EmailUpdateView,
                                        EmailDeleteView,
                                        serve_gcs_file
                                        )





# URLs define the mapping between URL patterns and view functions or classes.
# Django's URL dispatcher routes incoming HTTP requests to the appropriate view based on the requested URL.

#url_path, view_function, tag to identify url pattern. Use in exchange of url_path
 

urlpatterns = [

    path('email/', EmailListView.as_view(), name='email'),
    path('email/<int:pk>/', EmailDetailView.as_view(), name='email-detail'),
    path('import-file/', EmailCreateView.as_view(), name='import-file'),     #emailfileupload_form.html
    path('serve-file/<path:file_path>/', serve_gcs_file, name='serve_file'),
    path('email/<int:pk>/update/', EmailUpdateView.as_view(), name='email-update'),
    path('email/<int:pk>/delete/', EmailDeleteView.as_view(), name='email-delete'),
    path('', homepage_views.email_config_view, name='email_config_home'),
    path('send_emails/', homepage_views.send_emails_view, name='email_send'),
    path('file_uploads/', homepage_views.file_list, name='file_list'),
    path('upload_image_text_box/', homepage_views.upload_image_text_box, name='upload_image_text_box'),
    path('temp/', homepage_views.email_content_view, name='temp'),

]




# path('send-emails/', send_emails_view, name='send_emails_view')
# <a href="{% url 'send_emails_view' %}">Send Emails</a> 
# allows the path to be http://example.com/send-emails/

#example
# 'send-emails/' is the URL pattern. This means that when a user navigates to http://example.com/send-emails/, Django will call the send_emails_view function.
# send_emails_view is the view function associated with this URL pattern.
# 'send_emails_view' is the name of this URL pattern.


#Upload File Class Based is looking good 

#
#On file submission it stays on the same page, and provides success message
# On the same page you can utilze a dropdown to download the file or Update the selected file
#It will only display files for the given user

#Once selected from the dropdown the Update Current File routes you to the pagination
#Then allowing you to override the file and file_tag

#Once file is submitted in update page 
#It is then paginated routed from 
# http://localhost:8000/email/8/update/
# to
# http://localhost:8000/email/8/


# GOAL
#Based on uploaded files, parse the csv and 
#create a seperate form that pertains to those
#contents and display on the homepage


#Figure out where in the email send the csv is passed two 
#find way to integrate database into what customers are having
#emails sent to. 