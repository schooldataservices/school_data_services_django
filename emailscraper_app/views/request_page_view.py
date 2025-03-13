from django.shortcuts import render, redirect
from django.utils.html import escape
from django.contrib import messages
from django.http import JsonResponse
from ..forms import RequestConfigForm
from django.template.loader import render_to_string
from ..models import RequestConfig
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST, require_http_methods
from ..utils import send_request_email  # Import the new function
from django.contrib.auth.models import User
from django.db.models import Q

def filter_requests(request):
    user = request.GET.get('user', 'all')
    priority = request.GET.get('priority', 'all')
    date = request.GET.get('date', 'all')
    completion = request.GET.get('completion', 'all')

    filters = Q()
    
    if user != 'all':
        filters &= Q(creator__username=user)
    
    if priority != 'all':
        filters &= Q(priority_status=priority)
    
    if date != 'all':
        now = datetime.now()
        if date == 'today':
            filters &= Q(schedule_time__date=now.date())
        elif date == 'last7days':
            filters &= Q(schedule_time__gte=now - timedelta(days=7))
        elif date == 'thismonth':
            filters &= Q(schedule_time__year=now.year, schedule_time__month=now.month)
    
    if completion != 'all':
        completion_status = completion == 'true'
        filters &= Q(completion_status=completion_status)
    
    requests = RequestConfig.objects.filter(filters)
    
    data = []
    for req in requests:
        data.append({
            'id': req.id,
            'date_submitted': req.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
            'priority_status': req.priority_status,
            'schedule_time': req.schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
            'creator': req.creator.username,
            'email_content': req.email_content,
            'completion_status': 'Completed' if req.completion_status else 'Pending'
        })
    
    return JsonResponse({'requests': data})

def get_prior_requests_context(request):
    if request.user.is_authenticated:
        request_configs = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')  # Get only the logged-in user's configs
    else:
        request_configs = RequestConfig.objects.none()  # No requests for unauthenticated users

    # Apply filters
    priority_filter = request.GET.get('priority')
    date_filter = request.GET.get('date')
    completion_filter = request.GET.get('completion')

    if priority_filter and priority_filter != 'all':
        request_configs = request_configs.filter(priority_status=priority_filter)
    if completion_filter and completion_filter != 'all':
        request_configs = request_configs.filter(completion_status=(completion_filter == 'true'))
    if date_filter and date_filter != 'all':
        if date_filter == 'today':
            today = datetime.now().date()
            request_configs = request_configs.filter(schedule_time__date=today)
        elif date_filter == 'last7days':
            last_7_days = datetime.now().date() - timedelta(days=7)
            request_configs = request_configs.filter(schedule_time__date__gte=last_7_days)
        elif date_filter == 'thismonth':
            first_day_of_month = datetime.now().replace(day=1)
            request_configs = request_configs.filter(schedule_time__date__gte=first_day_of_month)

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

def create_request_config(request):
    context = get_prior_requests_context(request)  # For ajax requests with pagination, and filters

    if isinstance(context, JsonResponse):
        return context

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = RequestConfigForm(request.POST)
            if form.is_valid():
                # Save the form data to the database
                request_config = form.save(commit=False)
                if request.user.is_superuser and 'user_id' in request.POST:
                    try:
                        user = User.objects.get(id=request.POST['user_id'])
                        request_config.creator = user  # Set the selected user as the creator
                    except User.DoesNotExist:
                        context['error_message'] = escape("Selected user does not exist.")
                        context['form'] = form
                        return render(request, 'emailscraper_app/temp.html', context)
                else:
                    request_config.creator = request.user  # Set the logged-in user as the creator
                request_config.save()

                # Send email using the new function
                send_request_email(request_config, request.user)

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
        else:
            context['error_message'] = escape("You must be logged in to submit a request.")  # Prevent newlines

    # Initial page load, display RequestConfigForm with defaults
    else:
        context['form'] = RequestConfigForm()  # Ensure form is in context on GET request
        if request.user.is_superuser:
            context['users'] = User.objects.all()  # Pass all users to the template for admin

    return render(request, 'emailscraper_app/temp.html', context)

# View for dynamic AJAX changing of button changes
@login_required
@require_POST
def update_completion_status(request, config_id):
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

@login_required
@require_POST
def update_email_content(request, config_id):
    try:
        data = json.loads(request.body)
        email_content = data.get('email_content')
        config = RequestConfig.objects.get(id=config_id, creator=request.user)
        config.email_content = email_content
        config.save()
        return JsonResponse({'success': True})
    except RequestConfig.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Config not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["DELETE"])
def delete_request(request, config_id):
    try:
        config = RequestConfig.objects.get(id=config_id, creator=request.user)
        config.delete()
        return JsonResponse({'success': True})
    except RequestConfig.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Config not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})