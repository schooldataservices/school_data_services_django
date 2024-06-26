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


class EmailOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    sender_email = models.EmailField()
    message_body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now) #when email was initially sent
    updated_at = models.DateTimeField( auto_now=True)  #update everytime the Email was sent

    def __str__(self):
        return self.name
    
#FOR GCS BUCKET CUSTOMIZATION

# def user_directory_path(instance, filename):
#     # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
#     return 'user_{0}/{1}'.format(instance.user.id, filename)

# class MyModel(models.Model):
#     upload = models.FileField(upload_to=user_directory_path)


def upload_to(instance, filename):
    now = timezone.now()
    return f'uploads/{now.year}/{now.month}/{now.day}/{filename}'



class EmailFileUpload(models.Model):
   
    file_tag = models.CharField(max_length=150)
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(User, on_delete = models.CASCADE)
    column_names = models.TextField(blank=True)
    delimiter = models.CharField(max_length=1, default=',')
    body_rtf_2 =  RichTextField(null=True, blank=True)
    body_rtf_3 = RichTextUploadingField(blank=True, null=True)
    

    # date_posted = models.DateTimeField(default=timezone.now) 

    def __str__(self):
        return(self.file.name)
    

    def get_absolute_url(self):
        return reverse ('email-detail', kwargs={'pk': self.pk})   #returns full path as a string, and redirects to that page



