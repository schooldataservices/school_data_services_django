from django import forms
from .models import EmailSendsMetaData, EmailFileUpload, Customers
from config import email_config
import pandas as pd
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.widgets import CKEditorUploadingWidget

# Forms handle the validation and processing of user input from HTML forms.
# Django forms are Python classes that subclass django.forms.Form or django.forms.ModelForm.
# Forms define the fields and validation rules for user input, making it easy to handle form submissions.
# Forms can automatically generate HTML forms based on the defined fields, handle form validation, and sanitize user input.

class EmailBlastForm(forms.Form):
    email_options = forms.ModelChoiceField(queryset=EmailSendsMetaData.objects.all())


#Completely depends on config  
class EmailConfigForm(forms.Form):

    excluded_fields = {'EMAIL_PASS' : email_config.EMAIL_PASS}
         
    EMAIL_ADDRESS_FROM = forms.EmailField(initial=email_config.EMAIL_ADDRESS_FROM)
    EMAIL_PASS = forms.CharField(widget=forms.HiddenInput(), initial=email_config.EMAIL_PASS)  # Assuming it's a password field
    email_subject_line = forms.CharField(initial=email_config.email_subject_line)
    email_campaign_name = forms.CharField(initial=email_config.email_campaign_name)
    contact_column = forms.CharField(initial=email_config.contact_column)
    email_content = forms.CharField(widget=CKEditorUploadingWidget())

    def __init__(self, *args, **kwargs):
        super(EmailConfigForm, self).__init__(*args, **kwargs)
        # Exclude specified fields and mark them as not required

        for field_name in EmailConfigForm.excluded_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False




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

