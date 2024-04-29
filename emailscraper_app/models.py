from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django_ckeditor_5.fields import CKEditor5Field
#Whenever changes are made in models.py migrations must be made. This changes db schema
# python manage.py makemigrations
# python manage.py migrate

# Each model class represents a database table, and each attribute of the class 
# corresponds to a database field.

#Migrations allows us to make changes to the DB, even when there is existing data in the DB. 

#We can run the Django python shell to query the DB


class EmailOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    sender_email = models.EmailField()
    message_body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now) #when email was initially sent
    updated_at = models.DateTimeField( auto_now=True)  #update everytime the Email was sent

    def __str__(self):
        return self.name


class EmailFileUpload(models.Model):
   
    file_tag = models.CharField(max_length=150)
    file = models.FileField(upload_to='email_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, on_delete = models.CASCADE)
    column_names = models.TextField(blank=True)
    delimiter = models.CharField(max_length=1, default=',')
    body_rtf_2 = CKEditor5Field(null=True, blank=True, config_name='extends')
    

    # date_posted = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return(self.file)
    

    def get_absolute_url(self):
        return reverse ('email-detail', kwargs={'pk': self.pk})   #returns full path as a string, and redirects to that page



