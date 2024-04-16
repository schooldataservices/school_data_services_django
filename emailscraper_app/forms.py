from django import forms
from .models import EmailOption, EmailFileUpload
from config import email_config

# Forms handle the validation and processing of user input from HTML forms.
# Django forms are Python classes that subclass django.forms.Form or django.forms.ModelForm.
# Forms define the fields and validation rules for user input, making it easy to handle form submissions.
# Forms can automatically generate HTML forms based on the defined fields, handle form validation, and sanitize user input.

class EmailBlastForm(forms.Form):
    email_options = forms.ModelChoiceField(queryset=EmailOption.objects.all())

#Completely depends on config    

class EmailConfigForm(forms.Form):
                EMAIL_ADDRESS_FROM = forms.EmailField(initial=email_config.EMAIL_ADDRESS_FROM)
                EMAIL_PASS = forms.CharField(widget=forms.HiddenInput(), initial=email_config.EMAIL_PASS)  # Assuming it's a password field
                server = forms.CharField(initial=email_config.server)
                database = forms.CharField(initial=email_config.database)
                table_name = forms.CharField(initial=email_config.table_name)
                filter_date = forms.DateField(initial=email_config.filter_date)  # Assuming YYYY-MM-DD format
                email_subject_line = forms.CharField(initial=email_config.email_subject_line)
                email_campaign_name = forms.CharField(initial=email_config.email_campaign_name)
                contact_column = forms.CharField(initial=email_config.contact_column)
                sport = forms.CharField(initial=email_config.sport)
                db_pass = forms.CharField(widget=forms.HiddenInput(), initial = email_config.db_pass)  # Assuming it's a password field
                db_user = forms.CharField(initial=email_config.db_user)
                optional_iterated_columns = forms.CharField(initial=email_config.optional_iterated_columns, required=False)
                template_str = forms.CharField(initial=email_config.template_str)


class EmailFileForm(forms.ModelForm):
    class Meta:
        model = EmailFileUpload
        fields = ('file', 'file_tag')

        
                

                