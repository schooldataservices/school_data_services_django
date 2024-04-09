from django.db import models
from django.utils import timezone
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
    email = models.CharField(max_length=150)
    HighSchools = models.CharField(max_length=150)
    file = models.FileField(upload_to='EmailFiles/files/')

    def __str__(self):
        return(self.email)
