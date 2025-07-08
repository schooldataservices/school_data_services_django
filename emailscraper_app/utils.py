from django.conf import settings
from django.utils.html import strip_tags
from .models import EmailMetadata
from google.oauth2 import service_account
from googleapiclient.discovery import build
import tempfile
from emailscraper_proj.settings import django_hosting_json_file
import json
import os
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings


def send_request_email(request_config, user):
    subject = f'New Request Created from {user.username}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['schooldataservices.info@gmail.com', '2015samtaylor@gmail.com', user.email]

    # Plain text version (fallback)
    text_content = f"""
    Hello {user.username},

    A new request has been created with the following details:

    Priority Status: {request_config.priority_status}
    Completion Date: {request_config.schedule_time}
    Email Content: {strip_tags(request_config.email_content)}

    You can view the request details here:
    http://localhost:8000/historical-requests/?id={request_config.id}&user_id={user.username}&keyword=

    Thank you,
    School Data Services
    """

    # HTML version with richer formatting and logo
    html_content = f"""
    <html>
      <body>
        <p>Hello {user.username},</p>
        <p>A new request has been created with the following details:</p>
        <ul>
          <li><strong>Priority Status:</strong> {request_config.priority_status}</li>
          <li><strong>Completion Date:</strong> {request_config.schedule_time}</li>
          <li><strong>Email Content:</strong> {request_config.email_content}</li>
        </ul>
        <p>
          <a href="http://localhost:8000/historical-requests/?id={request_config.id}&user_id={user.username}&keyword=" target="_blank">
            View your request
          </a>
        </p>
        <p>Thank you,</p>
        <a href="https://schooldataservices.com" target="_blank" style="text-decoration:none;">
          <img src="https://storage.googleapis.com/django_hosting/base_images/favicon_sds_2.png" alt="Logo" width="85" style="border:none;outline:none;text-decoration:none;display:inline-block;" />
        </a>
        <br>
        <a href="https://schooldataservices.com" target="_blank" style="text-decoration:none; color:#000;">
          School Data Services
        </a>
        <p style="margin:0;padding:0;">Helping Schools Make Data Flow Easy</p>
      </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send(fail_silently=False)
    except Exception as e:
        print(f'Unable to send email due to error: {e}')

    # Record email metadata
    EmailMetadata.objects.create(
        user=user,
        priority_status=request_config.priority_status,
        schedule_time=request_config.schedule_time,
        email_content=request_config.email_content
    )


def record_email_metadata(request, email_config):
    """
    Create and save an EmailOption instance to record email metadata.
    """

#This must only be for samuel.taylor super user
def add_to_google_calendar(summary, description, start_datetime, end_datetime):
    # Your secret is a JSON string with escape characters, decode it
    raw_json_str = django_hosting_json_file
    try:
        service_account_dict = json.loads(raw_json_str)
    except json.JSONDecodeError as e:
        # print("Failed to decode JSON from secret:", e)
        return

    # Write the decoded JSON to a temp file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_json:
        json.dump(service_account_dict, temp_json)
        temp_json.flush()
        temp_json_path = temp_json.name

    try:
        creds = service_account.Credentials.from_service_account_file(
            temp_json_path,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=creds)

        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Chicago',
            },
        }

        created_event = service.events().insert(calendarId='2015samtaylor@gmail.com', body=event).execute()
        # print("Google Calendar event created:", created_event)
        return created_event.get('htmlLink')

    finally:
        os.remove(temp_json_path)  # Always clean up temp file
