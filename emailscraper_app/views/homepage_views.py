from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from ..forms import EmailBlastForm, EmailFileUploadForm
from ..models import EmailSendsMetaData, EmailFileUpload
from emailscraper_app.views.uploading_file_views import read_csv_from_gcs


import pandas as pd
from datetime import datetime
from config import *
from django.core.serializers.json import DjangoJSONEncoder
import json
from email_send_main import blast


def landing_page(request):
    return render(request, 'emailscraper_app/landing_page.html')


# views are Python functions or classes that receive HTTP requests and return HTTP responses.
# Views contain the business logic of your application, including data retrieval, processing, and rendering.
# Views interact with MODELS to retrieve or manipulate data and with templates to generate HTML output.



# def handle_email_config_form(request, form_data):
#     email_config_form = EmailConfigForm(request.POST or None, initial=form_data) #populate form, otherwise None
    
#     if request.method == 'POST' and email_config_form.is_valid():

#         form_data.update(email_config_form.cleaned_data)
#         request.session['email_config'] = form_data
#         print('Form data saved to session:', form_data)

#          # Retrieve and save selected file ID from live HTML
#         selected_file_id = request.POST.get('selected_file_id', None)
#         request.session['selected_file_id'] = selected_file_id

#         messages.success(request, 'Email configuration saved successfully.')
#         return(True, email_config_form)
#     else:
#         print('EmailConfigForm is invalid')
#         print(email_config_form.errors)

    # return(False, email_config_form)







def record_email_metadata(request, email_config):
    """
    Create and save an EmailOption instance to record email metadata.
    """
    user = request.user.username if request.user.is_authenticated else ''

    email_metadata = EmailSendsMetaData(
        creator_id = request.user,
        username=user,
        campaign = email_config.get('email_campaign_name'),
        subject=email_config.get('email_subject_line'),
        sender_email=email_config.get('EMAIL_ADDRESS_FROM', ''),
        message_body=email_config.get('email_content', ''),
    ) #created_at, and updated_at handled automatically

    email_metadata.save()
    print(f'Email metadata saved: {email_metadata}')




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


# def upload_image_text_box(request):
#     # Your existing code to initialize the form
#     email_config_form = EmailConfigForm()

#     # Check if the 'email_content' field should use CKEditor widget
#     use_ckeditor = True  # Determine this based on your conditions

#     return render(request, 'emailscraper_app/upload_image_text_box.html', {
#         'email_config_form': email_config_form,
#         'use_ckeditor': use_ckeditor,  # Pass the flag to the template
#     })


  
 

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



def format_datetime_fields(data):
    """
    Recursively format any datetime objects in a dictionary or list into strings.
    Ensures safe rendering in templates and JSON serialization.
    """
    if isinstance(data, dict):
        return {key: format_datetime_fields(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [format_datetime_fields(item) for item in data]
    elif isinstance(data, datetime):
        return data.strftime('%Y-%m-%d %H:%M:%S')
    return data



#-----------------------------Particular to Email Blast-------------------------------------------------------



# def email_config_requirements(request):
#     if request.method == 'POST':
#         form = EmailConfigForm(request.POST)
#         if form.is_valid():
#             # Access the selected priority status and schedule time
#             priority_status = form.cleaned_data['priority_status']
#             schedule_time = form.cleaned_data['schedule_time']
            
#             # You can now store this in the session or database as needed
#             # For example, store it in the session
#             request.session['priority_status'] = priority_status
#             request.session['schedule_time'] = schedule_time.isoformat()  # Save in ISO format

#             # After the form is saved, redirect to another view or show a success message
#             messages.success(request, f"Campaign scheduled for {schedule_time}.")
#             return redirect('success_url')  # Or wherever you want to redirect

#     else:
#         form = EmailConfigForm(initial={'priority_status': 'medium'})  # You can set default values

#     return render(request, 'emailscraper_app/landing_page.html', {'form': form})



@login_required
def send_emails_view(request):

      # Check if the priority_status exists in the session
    priority_status = request.session.get('priority_status', None)

    if not priority_status:
        # If no priority status is selected, prevent proceeding
        messages.error(request, "You must select a priority status before sending emails.")
        return redirect('email_config_home')  # Redirect to the email configuration page


    email_config = request.session.get('email_config') #get the variables from the session, if saved it will be overwritten
    print(f'Here is the email config from the session: {email_config}')

    if request.method == 'POST':
        

         # Provide prior upload files from GCS
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
            blast(email_config, df, request.user, test=True)          #make sure email_pass is coming across as encrypted or hidden. 
            messages.success(request, 'Emails sent successfully!')
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