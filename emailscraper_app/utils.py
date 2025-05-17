from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from .models import EmailMetadata

def send_request_email(request_config, user):
    subject = f'New Request Created from {user.username}'
    plain_message = (
        f'A new request has been created by {user.username}.\n\n'
        f'Priority Status: {request_config.priority_status}\n'
        f'Completion Date: {request_config.schedule_time}\n'
        f'Email Content: {strip_tags(request_config.email_content)}\n'
    )
    html_message = (
        f'<p>A new request has been created by {user.username}.</p>'
        f'<p>Priority Status: {request_config.priority_status}</p>'
        f'<p>Completion Date: {request_config.schedule_time}</p>'
        f'<p>Email Content: {request_config.email_content}</p>'
    )
    from_email = settings.EMAIL_HOST_USER  # Use the configured email host user
    recipient_list = ['schooldataservices.info@gmail.com', '2015samtaylor@gmail.com', user.email]
    try:
        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        print(f'Sending email to {recipient_list} with subject: {subject}')
    except Exception as e:
        print('Unable to send email due to error:', {e})

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
