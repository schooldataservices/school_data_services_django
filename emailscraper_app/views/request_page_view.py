from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from ..forms import  RequestConfigForm, EmailFileUploadForm
from ..models import RequestConfig
from django.contrib.auth.decorators import login_required

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

def get_prior_requests_context(request):
    request_configs = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')  # Get only the logged-in user's configs

    # Extract distinct priority statuses
    unique_priorities = set(request_configs.values_list("priority_status", flat=True))

    return {
        'request_configs': request_configs,
        'unique_priorities': unique_priorities,  # Pass unique priorities to the template
    }
    # return render(request, 'emailscraper_app/temp.html', context)


@login_required
def create_request_config(request):
    context = get_prior_requests_context(request)  # Load email configurations & welcome message no matter what by user

    if request.method == 'POST':
        form = RequestConfigForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            request_config = form.save(commit=False)
            request_config.creator = request.user  # Set the logged-in user as the creator
            request_config.save()

            # Update context to reflect the new data
            context = get_prior_requests_context(request)
            context['form'] = RequestConfigForm()  # Reset the form
            context['success_message'] = 'Request Submitted Successfully'

        #Form is invalid at this point due to empty fields
        else:
            context['form'] = form  # Keep the invalid form to show errors
            context['error_message'] = "Please correct the errors below."
 
    #Intial page load, display RequestConfigForm with defaults
    else:
        context['form'] = RequestConfigForm()  # Ensure form is in context on GET request

    return render(request, 'emailscraper_app/temp.html', context)


#View for dynamic AJAX changing of button changes
@login_required
def update_completion_status(request, config_id):
    if request.method == 'POST':
        try:
            # Get the RequestConfig object
            config = RequestConfig.objects.get(id=config_id)

            # Get the new completion status from the request data
            completion_status = request.POST.get('completion_status') == 'true'

            # Update the completion status of the config
            config.completion_status = completion_status
            config.save()

            # Respond with a success message
            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'RequestConfig not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})