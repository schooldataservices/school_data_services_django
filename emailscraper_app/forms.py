from django import forms
from .models import EmailOption
from config import imap_password_customplanet, db_password, db_username
from .modules.Sending_Emails.sends import SendMail

# Forms handle the validation and processing of user input from HTML forms.
# Django forms are Python classes that subclass django.forms.Form or django.forms.ModelForm.
# Forms define the fields and validation rules for user input, making it easy to handle form submissions.
# Forms can automatically generate HTML forms based on the defined fields, handle form validation, and sanitize user input.

class EmailBlastForm(forms.Form):
    email_options = forms.ModelChoiceField(queryset=EmailOption.objects.all())

# used for selecting a single model object from a queryset.
# retrieves all rows from the EmailOption model, in other words it pulls in all records from that tablle
    

class EmailConfigForm(forms.Form):
                EMAIL_ADDRESS_FROM = forms.EmailField(initial='2015samtaylor@gmail.com')
                EMAIL_PASS = forms.CharField(widget=forms.HiddenInput(), initial='B@dasspig1')  # Assuming it's a password field
                server = forms.CharField(initial='emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com')
                database = forms.CharField(initial='emailcampaign')
                table_name = forms.CharField(initial='email_history')
                filter_date = forms.DateField(initial='2024-03-04')  # Assuming YYYY-MM-DD format
                email_subject_line = forms.CharField(initial='Local Supplier for Baseball Apparel')
                email_campaign_name = forms.CharField(initial='Local Supplier Baseball')
                contact_column = forms.CharField(initial='email')
                sport = forms.CharField(initial='Baseball')
                db_pass = forms.CharField(widget=forms.HiddenInput(), initial = db_password)  # Assuming it's a password field
                db_user = forms.CharField(initial='admin')




                