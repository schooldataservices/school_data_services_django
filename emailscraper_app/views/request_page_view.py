from django.shortcuts import render
from django.utils.html import escape
from django.contrib import messages
from django.http import JsonResponse
from ..forms import  RequestConfigForm, EmailFileUploadForm
from django.template.loader import render_to_string
from ..models import RequestConfig
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

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

    # Apply filters
    priority_filter = request.GET.get('priority')
    date_filter = request.GET.get('date')
    completion_filter = request.GET.get('completion')

    if priority_filter and priority_filter != 'all':
        request_configs = request_configs.filter(priority_status=priority_filter)
    if completion_filter and completion_filter != 'all':
        request_configs = request_configs.filter(completion_status=(completion_filter == 'true'))
    if date_filter and date_filter != 'all':
        # Apply date filter logic here (e.g., filter by today, last 7 days, this month)
        pass

    # Extract distinct priority statuses
    unique_priorities = set(request_configs.values_list("priority_status", flat=True))
    unique_completion_status = set(request_configs.values_list("completion_status", flat=True))

    # Paginate the request_configs, 10 per page
    paginator = Paginator(request_configs, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'unique_priorities': unique_priorities,  # Pass unique priorities to the template
        'unique_completion_status': unique_completion_status
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('emailscraper_app/request_list.html', {'page_obj': page_obj}, request=request)
        return JsonResponse({
            'html': html.strip(),
            'total_results': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })

    return context

@login_required
def create_request_config(request):
    context = get_prior_requests_context(request)  # Load email configurations & welcome message no matter what by user

    if isinstance(context, JsonResponse):
        return context

    if request.method == 'POST':
        form = RequestConfigForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            request_config = form.save(commit=False)
            request_config.creator = request.user  # Set the logged-in user as the creator
            request_config.save()

            # Update context to reflect the new data
            context = get_prior_requests_context(request)
            if isinstance(context, JsonResponse):
                return context
            context['form'] = RequestConfigForm()  # Reset the form
            context['success_message'] = 'Request Submitted Successfully'

        # Form is invalid at this point due to empty fields
        else:
            context['form'] = form  # Keep the invalid form to show errors
            context['error_message'] = escape("Please correct the errors below.")  # Prevent newlines

    # Initial page load, display RequestConfigForm with defaults
    else:
        context['form'] = RequestConfigForm()  # Ensure form is in context on GET request

    return render(request, 'emailscraper_app/temp.html', context)

# View for dynamic AJAX changing of button changes
@login_required
def update_completion_status(request, config_id):
    if request.method == 'POST':
        # Get the status from the request body
        data = json.loads(request.body)
        completion_status = data.get('completion_status')
        
        # Get the config and update the status using AJAX
        try:
            config = RequestConfig.objects.get(id=config_id)
            config.completion_status = completion_status
            config.save()
            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Config not found'})