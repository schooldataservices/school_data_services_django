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
        ('normal', 'Normal'),
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
        default='normal',
    )
    email_content = RichTextUploadingField()
    schedule_time = models.DateTimeField()
    date_submitted = models.DateTimeField(auto_now_add=True) 
    completion_status = models.BooleanField(default=False)

    request_title = models.CharField(max_length=150, blank=False)  # short descriptive title

    reference_tag = models.CharField(
    max_length=50,
    blank=True,
    null=False,         
    unique=True
    )

    def __str__(self):
        return f"Email Configuration: {self.priority_status} |Request Completion Date {self.schedule_time} | Created by {self.creator.username} @ {self.date_submitted} "

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.reference_tag:
            # Get school acronym from user's profile
            school_acronym = self.creator.profile.school_acronym if self.creator and hasattr(self.creator, 'profile') else 'GEN'
            self.reference_tag = f"{school_acronym}-{self.id}"
            super().save(update_fields=['reference_tag'])


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


class Notification(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"