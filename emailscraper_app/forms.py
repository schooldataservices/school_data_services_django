from django import forms
from .models import EmailOption, EmailFileUpload
from config import email_config
import pandas as pd

# Forms handle the validation and processing of user input from HTML forms.
# Django forms are Python classes that subclass django.forms.Form or django.forms.ModelForm.
# Forms define the fields and validation rules for user input, making it easy to handle form submissions.
# Forms can automatically generate HTML forms based on the defined fields, handle form validation, and sanitize user input.

class EmailBlastForm(forms.Form):
    email_options = forms.ModelChoiceField(queryset=EmailOption.objects.all())

#Completely depends on config    

class EmailConfigForm(forms.Form):

    excluded_fields = {'EMAIL_PASS' : email_config.EMAIL_PASS,
                       'db_pass' : email_config.db_pass,
                       'db_user': email_config.db_user,
                       'table_name': email_config.table_name,
                       'server': email_config.server,
                       'database': email_config.database}
   
                
    EMAIL_ADDRESS_FROM = forms.EmailField(initial=email_config.EMAIL_ADDRESS_FROM)
    EMAIL_PASS = forms.CharField(widget=forms.HiddenInput(), initial=email_config.EMAIL_PASS)  # Assuming it's a password field
    server = forms.CharField(widget=forms.HiddenInput(), initial=email_config.server)
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


    def __init__(self, *args, **kwargs):
        super(EmailConfigForm, self).__init__(*args, **kwargs)
        # Exclude specified fields and mark them as not required

        for field_name in EmailConfigForm.excluded_fields:
            if field_name in self.fields:
                self.fields[field_name].required = False

                

class EmailFileForm(forms.ModelForm):
    class Meta:
        model = EmailFileUpload
        fields = ('file', 'file_tag')

    def save(self, commit=True):

        print('Save triggered')

        instance = super().save(commit=False)
        uploaded_file = instance.file
        delimiter = instance.delimiter
        
        # Parse the uploaded file using pandas
        try:
            df = pd.read_csv(uploaded_file, delimiter=delimiter)
            print(df.head())
        except pd.errors.ParserError as e:
            raise forms.ValidationError(f"Error parsing file: {e}")
            print('Did not read csv')

        # Extract column names and save them to the model
        instance.column_names = ','.join(df.columns)

        if commit:
            instance.save()

        return instance


        
                

                