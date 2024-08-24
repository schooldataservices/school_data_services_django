from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from django.contrib.auth.models import User
from ..forms import EmailBlastForm, EmailConfigForm, EmailFileUploadForm
from ..models import EmailSendsMetaData, EmailFileUpload
from emailscraper_app.views.uploading_file_views import read_csv_from_gcs

import pandas as pd
from io import StringIO
import requests
from config import *
from emailscraper_app.modules.Sending_Emails import KC_schools
from email_send_main import blast

df = KC_schools.read_in()
df = KC_schools.filter_emails_by_sport(df, ['Baseball', 'Softball'])



# views are Python functions or classes that receive HTTP requests and return HTTP responses.
# Views contain the business logic of your application, including data retrieval, processing, and rendering.
# Views interact with MODELS to retrieve or manipulate data and with templates to generate HTML output.



def handle_email_config_form(request, form_data):
    email_config_form = EmailConfigForm(request.POST or None, initial=form_data)
    
    if request.method == 'POST' and email_config_form.is_valid():
        # filter_date = email_config_form.cleaned_data['filter_date'].strftime('%Y-%m-%d')
        # email_config_form.cleaned_data['filter_date'] = filter_date

        form_data.update(email_config_form.cleaned_data)
        request.session['email_config'] = form_data
        print('Form data saved to session:', form_data)

         # Retrieve and save selected file ID from live HTML
        selected_file_id = request.POST.get('selected_file_id', None)
        request.session['selected_file_id'] = selected_file_id

        messages.success(request, 'Email configuration saved successfully.')
        return True, email_config_form
    else:
        print('EmailConfigForm is invalid')
        print(email_config_form.errors)

    return(False, email_config_form)


def handle_email_file_upload_form(request):
    email_file_upload_form = EmailFileUploadForm(request.POST or None, request.FILES or None)
    
    if request.method == 'POST' and email_file_upload_form.is_valid():
        email_file_upload_form.save()
        messages.success(request, 'Email file uploaded successfully.')
        return True, email_file_upload_form
    else:
        print('EmailFileUploadForm is invalid')
        print(email_file_upload_form.errors)

    return False, email_file_upload_form



@login_required
def email_config_view(request):
    excluded_fields = ['EMAIL_PASS', 'db_pass', 'db_user', 'table_name', 'server', 'database']
    
    form_data = request.session.get('email_config', {})
    email_config_saved, email_config_form = handle_email_config_form(request, form_data)
    email_file_uploaded, email_file_upload_form = handle_email_file_upload_form(request)
    
    #For determnining what file shows up in the dropdown on page reload
    selected_file_id = int(request.session.get('selected_file_id', 0))
    

    if email_config_saved or email_file_uploaded:
        return redirect('email_config_home')
    
    for field_name in excluded_fields:
        if field_name in email_config_form.fields:
            del email_config_form.fields[field_name]

    # Use the separate function to get email fcontext
    email_context = get_email_context(request.user)
    emails_sent = request.session.get('emails_sent', False)
    previous_files = EmailFileUpload.objects.filter(creator_id=request.user.id)
    
    for file in previous_files:
        file.file_path = file.file.name

    context = {
        'email_context': email_context,
        'email_config_form': email_config_form,
        'email_file_upload_form': email_file_upload_form,
        'previous_files': previous_files,
        'selected_file_id': selected_file_id,
        'emails': email_context['emails'],  # Pass the emails to the template
    }

    return render(request, 'emailscraper_app/homepage_base.html', context)



def get_email_context(user):
    emails = EmailSendsMetaData.objects.all()
    profile_name = user.profile.user.username if hasattr(user, 'profile') else None
    first_time_login = user.last_login is None
    welcome_message = f'Welcome to the party, {profile_name}!' if first_time_login else f'Welcome back, {profile_name}!'
    
    return {
        'emails': emails,
        'profile_name': profile_name,
        'welcome_message': welcome_message,
    }



def record_email_metadata(request, email_config):
    """
    Create and save an EmailOption instance to record email metadata.
    """
    user = request.user.username if request.user.is_authenticated else ''

    email_metadata = EmailSendsMetaData(
        username=user,
        campaign = email_config.get('email_campaign_name'),
        subject=email_config.get('email_subject_line'),
        sender_email=email_config.get('EMAIL_ADDRESS_FROM', ''),
        message_body=email_config.get('email_content', ''),
    ) #created_at, and updated_at handled automatically

    email_metadata.save()
    print(f'Email metadata saved: {email_metadata}')




def send_emails_view(request):


    email_config = request.session.get('email_config') #get the variables from the session, if saved it will be overwritten
    print(f'Here is the email config from the session: {email_config}')

    if request.method == 'POST':
        
        #add in the db configurations, server, db info
        for key, value in EmailConfigForm.excluded_fields.items():
            email_config[key] = value

         # Get the selected file URL and extract the part needed
        selected_file_url = request.POST.get('selected_file_url')
        print(f'Here is the selected file url {selected_file_url}')
        if selected_file_url.startswith('/serve-file/'):
            selected_file_url = selected_file_url[len('/serve-file/'):]

        # Remove any trailing slash to read from GCS
        selected_file_url = selected_file_url.rstrip('/')
        print(f'Selected file URL: {selected_file_url}')

        try:
            df = read_csv_from_gcs(request, selected_file_url, pandas_request=True)
            if df is None:
                raise ValueError('DataFrame is None. File could not be read.')
            print('Read in file properly')
        except Exception as e:
            print(f'Unable to read file due to {e}')
            messages.error(request, f'Error reading file: {e}')
            return redirect('email_config_home')


        # Call the blast function with the email configuration and the dataframe
        try:
            blast(email_config, df, request.user, test=True)
            messages.success(request, 'Emails sent successfully!')
            print(f'Here is the email_config in the try block {email_config}')
            record_email_metadata(request, email_config)
        except Exception as e:
            print(f'Error during email blast: {e}')
            messages.error(request, f'Error sending emails: {e}')
            return redirect('email_config_home')

        # Redirect to the homepage URL
        return redirect('email_config_home')

    else:
        form = EmailBlastForm()

    return render(request, 'emailscraper_app/homepage_base.html', {'form': form})





def file_list(request):

    if request.method == 'POST':
        form = EmailFileUpload(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = EmailFileUpload()

    context = {
        'files' : EmailFileUpload.objects.all(),
        'form': form
    }
    return render(request, 'emailscraper_app/file_list.html', context)


def upload_image_text_box(request):
    # Your existing code to initialize the form
    email_config_form = EmailConfigForm()

    # Check if the 'email_content' field should use CKEditor widget
    use_ckeditor = True  # Determine this based on your conditions

    return render(request, 'emailscraper_app/upload_image_text_box.html', {
        'email_config_form': email_config_form,
        'use_ckeditor': use_ckeditor,  # Pass the flag to the template
    })


  
 

def email_content_view(request):
    emailfileupload = EmailFileUpload.objects.all()

    return render(request, 'emailscraper_app/emailfileupload_form.html', {'emailfileupload': emailfileupload})




def serve_image(request):
    bucket_name = 'django_hosting'
    image_name = 'default.jpg'
    
    # Initialize Google Cloud Storage client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(image_name)
    
    # Download image data
    image_data = blob.download_as_bytes()
    
    # Return image data as HTTP response
    return HttpResponse(image_data, content_type='image/jpeg')

