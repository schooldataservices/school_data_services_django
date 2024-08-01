from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from ..forms import EmailBlastForm, EmailConfigForm, EmailFileUploadForm
from ..models import EmailOption, EmailFileUpload


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
        filter_date = email_config_form.cleaned_data['filter_date'].strftime('%Y-%m-%d')
        email_config_form.cleaned_data['filter_date'] = filter_date

        form_data.update(email_config_form.cleaned_data)
        request.session['email_config'] = form_data
        print('Form data saved to session:', form_data)

        messages.success(request, 'Email configuration saved successfully.')
        return True, email_config_form
    else:
        print('EmailConfigForm is invalid')
        print(email_config_form.errors)

    return False, email_config_form


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

    if email_config_saved or email_file_uploaded:
        return redirect('email_config_home')
    
    for field_name in excluded_fields:
        if field_name in email_config_form.fields:
            del email_config_form.fields[field_name]

    emails = EmailOption.objects.all()
    profile_name = request.user.profile.user.username if hasattr(request.user, 'profile') else None
    first_time_login = request.user.last_login is None
    welcome_message = f'Welcome to the party, {request.user.username}!' if first_time_login else f'Welcome back, {profile_name}!'

    emails_sent = request.session.get('emails_sent', False)
    previous_files = EmailFileUpload.objects.filter(creator_id=request.user.id)
    
    for file in previous_files:
        file.file_path = file.file.name  # Use the file's name as the path

    context = {
        'email_context': {
            'welcome_message': welcome_message,
            'emails_sent': emails_sent,
        },
        'email_config_form': email_config_form,
        'email_file_upload_form': email_file_upload_form,
        'previous_files': previous_files,

        'emails': emails,
    }
    return render(request, 'emailscraper_app/homepage_base.html', context)



    




def send_emails_view(request):

    #here is the email_config dict passed into process {'email_content': '<p>dfsadafsddassdfs</p>', 'EMAIL_PASS': 'feqdwowrmaqthjkx', 'db_pass': 'Pretty11', 'db_user': 'admin', 'table_name': 'email_history', 'server': 'emailcampaign.c9vhoi6ncot7.us-east-1.rds.amazonaws.com', 'database': 'emailcampaign'}

    email_config = request.session.get('email_config') #get the variables from the session, if saved it will be overwritten
    print(f'Here is the email config from the session: {email_config}')
    print('Send emails view has been called')

    if request.method == 'POST':

        for key, value in EmailConfigForm.excluded_fields.items():
            email_config[key] = value

        # Call the blast function from email_send_main.py, df can be configured to be passed in dynamically with the adlibs
        #currently reads df from views file being a global variable
        blast(email_config, df, test=True)

        messages.success(request, 'Emails sent successfully!')
        
        # Redirect to the homepage URL
        return redirect('email_config_home')
    
    else: #on initial page load
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
