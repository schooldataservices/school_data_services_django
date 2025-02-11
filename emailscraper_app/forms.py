from django import forms
from .models import EmailSendsMetaData, EmailFileUpload, Customers, RequestConfig

# import sys
# import os  # Add the parent directory (emailscraper_proj) to the sys.path to make it importable
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'emailscraper_proj')))

from .email_setup import *
import pandas as pd
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

# Forms handle the validation and processing of user input from HTML forms.
# Django forms are Python classes that subclass django.forms.Form or django.forms.ModelForm.
# Forms define the fields and validation rules for user input, making it easy to handle form submissions.
# Forms can automatically generate HTML forms based on the defined fields, handle form validation, and sanitize user input.

class EmailBlastForm(forms.Form):
    email_options = forms.ModelChoiceField(queryset=EmailSendsMetaData.objects.all())



class RequestConfigForm(forms.ModelForm):
    class Meta:
        model = RequestConfig
        fields = ['priority_status', 'schedule_time', 'email_content', 'completion_status']

    priority_status = forms.ChoiceField(
        choices=RequestConfig.PRIORITY_CHOICES,  # Ensure this matches your model choices
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Priority status is required.'}
    )

    schedule_time = forms.DateTimeField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'datetimepicker form-control', 'placeholder': 'Select a date'}),
        error_messages={'required': 'Select the desired completion date.'}
    )



class EmailFileUploadForm(forms.ModelForm):

    class Meta:

        model = EmailFileUpload
        fields = ['file_tag', 'file', 'creator_id', 'column_names', 'delimiter']



class EmailFileForm(forms.ModelForm):
    class Meta:
        model = EmailFileUpload
        fields = ('file', 'file_tag', 'delimiter')




class EmailContentForm(forms.Form):
    email_content = forms.CharField(widget=CKEditorUploadingWidget(), label='Email Content')


            
class CustomersForm(forms.ModelForm):
    class Meta:
        model = Customers
        exclude = ['creator_id']

