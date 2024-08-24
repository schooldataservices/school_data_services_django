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
    creator_id = models.ForeignKey(User, on_delete = models.CASCADE, db_column='creator_id') # maps to the User model's primary key).
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

    creator_id = models.ForeignKey(User, on_delete= models.CASCADE, db_column='creator_id')
    email_recipient = models.EmailField()
    date_sent = models.DateTimeField()
    subject = models.CharField(max_length=255)
    contact_column = models.CharField(max_length=255)
    from_email = models.EmailField()
    email_campaign_tag = models.CharField(max_length=255)

    def __str__(self):
        return f"Email to {self.email_recipient} on {self.date_sent}"