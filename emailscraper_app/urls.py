from django.urls import path
from . import views
from .views import (EmailListView,
                    EmailDetailView, 
                    EmailCreateView,
                    EmailUpdateView)


# URLs define the mapping between URL patterns and view functions or classes.
# Django's URL dispatcher routes incoming HTTP requests to the appropriate view based on the requested URL.

#url_path, view_function, tag to identify url pattern. Use in exchange of url_path
 

urlpatterns = [

    path('', views.initial_view, name='initial_view'),
    path('email/', EmailListView.as_view(), name='email'),
    path('email/<int:pk>/', EmailDetailView.as_view(), name='email-detail'),
    path('email/new/', EmailCreateView.as_view(), name='email-create'),     #class based
    path('email/<int:pk>/update/', EmailUpdateView.as_view(), name='email-update'),


    path('email_config/', views.email_config_view, name='email_config_home'),
    path('send_emails/', views.send_emails_view, name='email_send'),
    path('upload_file/', views.upload_file, name='upload'),                  #custom based
    path('file_list/', views.file_list, name='file_list'),

    # path('file_list/upload_file/', views.upload_file, name='upload_file'),
]



# path('send-emails/', send_emails_view, name='send_emails_view')
# <a href="{% url 'send_emails_view' %}">Send Emails</a> 
# allows the path to be http://example.com/send-emails/

#example
# 'send-emails/' is the URL pattern. This means that when a user navigates to http://example.com/send-emails/, Django will call the send_emails_view function.
# send_emails_view is the view function associated with this URL pattern.
# 'send_emails_view' is the name of this URL pattern.

#Has previously updated files dropdown
# http://localhost:8000/email/1/update/


#
# http://localhost:8000/email/new/


#Change once the file is submitted just pop a success message