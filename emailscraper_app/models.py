from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField


    
def upload_to(instance, filename):
    now = timezone.now()
    return f'uploads/{now.year}/{now.month}/{now.day}/{filename}'


class RequestConfig(models.Model):
    # Priority Status choices
    PRIORITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    creator = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Deletes requests if user is deleted
        related_name='request_configs',  # Allows reverse lookup
        null=True,  # Temporarily allow NULL values for migration
        blank=True  # Allow empty values when creating a form
    )

    priority_status = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
    )
    email_content = RichTextUploadingField()
    schedule_time = models.DateTimeField()
    date_submitted = models.DateTimeField(auto_now_add=True) 
    completion_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Email Configuration: {self.priority_status} |Request Completion Date {self.schedule_time} | Created by {self.creator.username} @ {self.date_submitted} "


class Email(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class EmailMetadata(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    priority_status = models.CharField(max_length=10)
    schedule_time = models.DateTimeField()
    email_content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email sent by {self.user.username} with priority {self.priority_status} on {self.date_sent}"
