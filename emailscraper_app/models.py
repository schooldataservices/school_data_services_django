from django.db import models
#Whenever changes are made in models.py migrations must be made. This changes db schema

# Each model class represents a database table, and each attribute of the class 
# corresponds to a database field.


class MyModel(models.Model):
    name = models.CharField(max_length=100)  # CharField in the db with max length of 100 characters
    description = models.TextField()  #TextField in the db 

    def __str__(self):
        return self.name
    
    # my_instance = MyModel(name='Example', description='This is an example')
    #calling an instance represents a row of the database table



class EmailOption(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    sender_email = models.EmailField()
    message_body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

