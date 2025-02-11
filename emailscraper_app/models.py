from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
#Whenever changes are made in models.py migrations must be made. This changes db schema
# python manage.py makemigrations
# python manage.py migrate
# Each model class represents a database table, and each attribute of the class 
# corresponds to a database field.
#Migrations allows us to make changes to the DB, even when there is existing data in the DB. 
#We can run the Django python shell to query the DB


class EmailSendsMetaData(models.Model):
    creator_id = models.ForeignKey(User, on_delete = models.SET_DEFAULT, default=1, db_column='creator_id')
    username = models.CharField(max_length=255)
    campaign = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    sender_email = models.EmailField()
    message_body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # when email was initially sent
    updated_at = models.DateTimeField(auto_now=True)  # update every time the Email was sent

    def __str__(self):
        return self.username  # or another field that makes sense for identifying the record

    

def upload_to(instance, filename):
    now = timezone.now()
    return f'uploads/{now.year}/{now.month}/{now.day}/{filename}'



class EmailFileUpload(models.Model):
   
    file_tag = models.CharField(max_length=150)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, on_delete = models.SET_DEFAULT, default=1, db_column='creator_id') # maps to the User model's primary key, is user deleted, set defauly val to 00 in EmailFileUpload table
    column_names = models.TextField(blank=True)
    delimiter = models.CharField(max_length=2, default=',')    

    def __str__(self):
        return(self.file.name)
    

    def get_absolute_url(self):
        return reverse ('email-detail', kwargs={'pk': self.pk})   #returns full path as a string, and redirects to that page



#Need to record the emails sent in blast function to a table. Created the model. 
#Then reference the emails being passed in one by one. 
#Just need username and subject to be able to match up

class RecordingEmailRecipients(models.Model):

    creator_id = models.ForeignKey(User, on_delete = models.SET_DEFAULT, default=1, db_column='creator_id')
    email_recipient = models.EmailField()
    date_sent = models.DateTimeField()
    subject = models.CharField(max_length=255)
    contact_column = models.CharField(max_length=255)
    from_email = models.EmailField()
    email_campaign_tag = models.CharField(max_length=255)

    def __str__(self):
        return f"Email to {self.email_recipient} on {self.date_sent}"
    
    

class Customers(models.Model):
    creator_id = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1000000, db_column='creator_id')
    contact = models.CharField(max_length=150)  
    company = models.CharField(max_length=150) 
    title = models.CharField(max_length=100, blank=True, null=True) 
    department = models.CharField(max_length=100, blank=True, null=True)  
    salutation = models.CharField(max_length=50, blank=True, null=True) 
    phone = models.CharField(max_length=20, blank=True, null=True) 
    mobile = models.CharField(max_length=20, blank=True, null=True) 
    email = models.EmailField(blank=False, null=False)
    address = models.CharField(max_length=255, blank=True, null=True) 
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)  
    ZIP = models.CharField(max_length=10, blank=True, null=True)  
    county = models.CharField(max_length=100, blank=True, null=True)  
    fax = models.CharField(max_length=20, blank=True, null=True) 
    web_site = models.CharField(max_length=150, blank=True, null=True) 
    notes = models.TextField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'creator_id'],
                name='unique_email_creator'
            ),
        ]

    def __str__(self):
        return self.company  # This will return the company name as the string representation of the object



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
    email_content = models.TextField()
    schedule_time = models.DateTimeField()
    date_submitted = models.DateTimeField(auto_now_add=True) 
    completion_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Email Configuration: {self.priority_status} |Request Completion Date {self.schedule_time} | Created by {self.creator.username} @ {self.date_submitted} "
