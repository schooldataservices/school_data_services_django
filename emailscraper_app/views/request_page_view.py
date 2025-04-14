from django.shortcuts import render, redirect
from django.utils.html import escape
from django.contrib import messages
from django.http import JsonResponse
from ..forms import RequestConfigForm
from django.db import transaction
from django.template.loader import render_to_string
from ..models import RequestConfig, Notification
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST, require_http_methods
from ..utils import send_request_email  # Import the new function
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage

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
        if request.user.is_superuser:
            request_configs = RequestConfig.objects.all().order_by('-date_submitted')  # Get all configs for superuser
        else:
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

    # Extract distinct priority statuses and completion statuses
    if request.user.is_superuser:
        unique_priorities = set(RequestConfig.objects.values_list("priority_status", flat=True))
        unique_completion_status = set(RequestConfig.objects.values_list("completion_status", flat=True))
    else:
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


def paginate_requests(request, queryset, per_page=10):
    """
    Handles pagination for a given queryset.

    Args:
        request: The HTTP request object.
        queryset: The queryset to paginate.
        per_page: Number of items per page (default is 10).

    Returns:
        A dictionary containing the paginated page object and pagination metadata.
    """
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)  # Return the last page if out of range

    return {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'total_results': paginator.count,
        'current_page': page_obj.number,
    }


@transaction.atomic
def create_request_config(request):
    # Get the base queryset
    if request.user.is_authenticated:
        if request.user.is_superuser:
            request_configs = RequestConfig.objects.all().order_by('-date_submitted')  # All requests for superuser
        else:
            request_configs = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')  # Only user's requests
    else:
        request_configs = RequestConfig.objects.none()  # No requests for unauthenticated users

    # Apply filters (if any)
    priority_filter = request.GET.get('priority', 'all')
    date_filter = request.GET.get('date', 'all')
    completion_filter = request.GET.get('completion', 'all')

    if priority_filter != 'all':
        request_configs = request_configs.filter(priority_status=priority_filter)
    if completion_filter != 'all':
        request_configs = request_configs.filter(completion_status=(completion_filter == 'true'))
    if date_filter != 'all':
        if date_filter == 'today':
            today = datetime.now().date()
            request_configs = request_configs.filter(schedule_time__date=today)
        elif date_filter == 'last7days':
            last_7_days = datetime.now().date() - timedelta(days=7)
            request_configs = request_configs.filter(schedule_time__date__gte=last_7_days)
        elif date_filter == 'thismonth':
            first_day_of_month = datetime.now().replace(day=1)
            request_configs = request_configs.filter(schedule_time__date__gte=first_day_of_month)

    # Paginate the filtered queryset
    pagination_context = paginate_requests(request, request_configs)

    # Handle AJAX requests for pagination
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('emailscraper_app/request_list.html', {'page_obj': pagination_context['page_obj']}, request=request)
        return JsonResponse({
            'html': html.strip(),
            'total_results': pagination_context['total_results'],
            'total_pages': pagination_context['total_pages'],
            'current_page': pagination_context['current_page'],
        })

    # Handle POST request for creating a new request
    if request.method == 'POST':
        print("Handling POST request.")
        if request.user.is_authenticated:
            form = RequestConfigForm(request.POST)
            if form.is_valid():
                print("Form is valid, saving the form data.")
                # Save the form data to the database
                request_config = form.save(commit=False)

                # Check if "Submit on behalf of" has a value. Make them the creator
                user_id = request.POST.get('user_id')
                if request.user.is_superuser and user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request_config.creator = user  # Override creator with selected user
                        print(f"User {user} selected as creator.")
                    except User.DoesNotExist:
                        print(f"User with id {user_id} does not exist.")
                        context = {
                            'form': form,
                            'error_message': escape("Selected user does not exist."),
                        }
                        return render(request, 'emailscraper_app/submit_request.html', context)
                else:
                    request_config.creator = request.user  # Default to logged-in user
                    print(f"Logged-in user {request.user} set as creator.")

                request_config.save()

                # Send email using the new function
                send_request_email(request_config, request_config.creator)

                # Update context to reflect the new data
                pagination_context = paginate_requests(request, RequestConfig.objects.all().order_by('-date_submitted'))
                context = {
                    'form': RequestConfigForm(),  # Reset the form
                    'success_message': 'Request Submitted Successfully',
                    'page_obj': pagination_context['page_obj'],
                    'total_pages': pagination_context['total_pages'],
                    'total_results': pagination_context['total_results'],
                }
                return render(request, 'emailscraper_app/submit_request.html', context)

            else:
                context = {
                    'form': form,  # Keep the invalid form to show errors
                    'error_message': escape("Please correct the errors below."),
                }
                return render(request, 'emailscraper_app/submit_request.html', context)

        else:
            context = {
                'error_message': escape("You must be logged in to submit a request."),
            }
            return render(request, 'emailscraper_app/submit_request.html', context)

    # Handle GET request
    context = {
        'form': RequestConfigForm(),
        'page_obj': pagination_context['page_obj'],
        'total_pages': pagination_context['total_pages'],
        'total_results': pagination_context['total_results'],
    }
    if request.user.is_superuser:
        context['users'] = User.objects.all()  # Pass all users to the template for admin

    return render(request, 'emailscraper_app/submit_request.html', context)

@csrf_exempt
def update_email_content(request, request_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email_content = data.get('email_content', '').strip()

            # Update the email content in the database
            request_config = RequestConfig.objects.get(id=request_id)
            request_config.email_content = email_content
            request_config.save()

            # Create a notification for the change
            notification = Notification.objects.create(
                user=request.user,
                message=f"Email content for request '{request_config.id}' has been updated."
            )
            print(f"Notification created: {notification}")

            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_request(request, config_id):
    try:
        # Fetch the request config and delete it
        config = RequestConfig.objects.get(id=config_id)
        config.delete()

        Notification.objects.create(
            user=request.user,
            message=f"Request '{config_id}' has been deleted."
        )

        return JsonResponse({'success': True})
    except RequestConfig.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def update_completion_status(request, config_id):
    print(f"Received request to update completion status for config ID: {config_id}")
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Request data: {data}")
            completion_status = data.get('completion_status', False)

            # Update the database
            config = RequestConfig.objects.get(id=config_id)
            print(f"Found RequestConfig: {config}")
            config.completion_status = completion_status
            config.save()
            print(f"Updated completion status to: {completion_status}")

            # Create a notification for the change
            notification = Notification.objects.create(
                user=request.user,
                message=f"Request '{config_id}' has been {'completed' if completion_status else 'marked as pending'}."
            )
            print(f"Notification created: {notification}")

            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            print(f"RequestConfig with ID {config_id} does not exist.")
            return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
        except Exception as e:
            print(f"An error occurred: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    print("Invalid request method")
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)