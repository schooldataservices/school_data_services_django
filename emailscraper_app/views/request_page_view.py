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
from django.utils.timezone import now

def apply_filters(request, base_queryset):
    user = request.GET.get('user', None)
    priority = request.GET.get('priority', 'all')
    date = request.GET.get('date', 'all')
    completion = request.GET.get('completion', 'all')

    # Start with an empty Q object (no filters applied yet)
    filters = Q()

    # Filter by user
    if user and user != 'all':
        filters &= Q(creator__username=user)

    # Filter by priority
    if priority != 'all':
        filters &= Q(priority_status=priority)

    # Filter by completion status
    if completion != 'all':
        is_completed = completion.lower() == 'true'
        filters &= Q(completion_status=is_completed)

    # Filter by desired completion date
    if date != 'all':
        now = datetime.now()
        if date == 'today':
            filters &= Q(schedule_time__date=now.date())
        elif date == 'last7days':
                now = datetime.now()
                print(f"Current datetime (now): {now}")
                print(f"Datetime 7 days ago: {now - timedelta(days=7)}")
                filters &= Q(schedule_time__gte=now - timedelta(days=7))
        elif date == 'thismonth':
            filters &= Q(schedule_time__year=now.year, schedule_time__month=now.month)
    
    filtered_queryset = base_queryset.filter(filters)

    # Apply the filters to the base queryset
    return base_queryset.filter(filters)



def filter_requests(request):
    base_queryset = RequestConfig.objects.all()
    filtered_queryset = apply_filters(request, base_queryset)
  
    # Paginate the filtered queryset
    paginator = Paginator(filtered_queryset, 10)  # Show 10 requests per page
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        return JsonResponse({'error': 'Invalid page number'}, status=400)

    # Serialize the filtered requests
    data = {
        'requests': [
            {
                'id': req.id,
                'date_submitted': req.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
                'priority_status': req.priority_status,
                'schedule_time': req.schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                'creator': req.creator.username,
                'email_content': req.email_content,
                'completion_status': 'Completed' if req.completion_status else 'Pending',
            }
            for req in page_obj
        ],
        'users': list(User.objects.values_list('username', flat=True)) if request.user.is_superuser else [],
        'total_results': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }
    return JsonResponse(data)


#This defaults to the js when changing filters. Only called on page load
def get_prior_requests_context(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            base_queryset = RequestConfig.objects.all().order_by('-date_submitted')  # Get all configs for superuser
        else:
            base_queryset = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')  # Get only the logged-in user's configs
    else:
        base_queryset = RequestConfig.objects.none()  # No requests for unauthenticated users

    # Apply filters
    filtered_queryset = apply_filters(request, base_queryset)

    # Paginate the filtered queryset
    paginator = Paginator(filtered_queryset, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'total_results': paginator.count,
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
    # Get the base queryset based on user authentication
    if request.user.is_authenticated:
        if request.user.is_superuser:
            base_queryset = RequestConfig.objects.all().order_by('-date_submitted')  # All requests for superuser
        else:
            base_queryset = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')  # Only user's requests
    else:
        base_queryset = RequestConfig.objects.none()  # No requests for unauthenticated users

    # Apply filters to the base queryset
    filtered_queryset = apply_filters(request, base_queryset)

    # Paginate the filtered queryset
    pagination_context = paginate_requests(request, filtered_queryset)

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
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {request.body}")
    if request.method == 'POST':
        try:
            # Debug: Log the raw request body
            print(f"Raw request body: {request.body}")

            # Parse the JSON payload
            data = json.loads(request.body)
            print(f"Parsed JSON payload: {data}")  # Debug: Log the parsed JSON payload

            email_content = data.get('email_content', '').strip()
            selected_user_username = data.get('userFilter')  # Get userFilter from JSON payload
            print(f"Here is the selected user from userFilter: {selected_user_username}")

            # Update the email content in the database
            request_config = RequestConfig.objects.get(id=request_id)
            request_config.email_content = email_content
            request_config.save()

            # Call the create_notifications function
            create_notifications(
                logged_in_user=request.user,
                selected_user_username=selected_user_username,
                request_id=request_config.id,
                user_message=f"Email content for request id '{request_config.id}' has been updated."
            )

            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
        except Exception as e:
            print(f"Error in update_email_content: {e}")  # Debug: Log the exception
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
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    print(f"Request body: {request.body}")
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



def create_notifications(logged_in_user, selected_user_username, request_id,  user_message):
    """
    Creates notifications for the logged-in user and the selected user (if applicable).

    Args:
        logged_in_user (User): The currently logged-in user.
        selected_user_username (str): The username of the selected user from the dropdown.
        request_id (int): The ID of the request being processed.
        superuser_message (str): The notification message for the superuser.
        user_message (str): The notification message for the selected user.

    Returns:
        None
    """
    print(f"Creating notifications...")
    print(f"Logged-in user: {logged_in_user.username}")
    print(f"Selected user from dropdown: {selected_user_username}")
    print(f"Request ID: {request_id}")
    print(f"Message: {user_message}")
    
    # Create a notification for the logged-in user
    Notification.objects.create(
        user=logged_in_user,
        message=user_message,
    )
    print(f"Notification created for logged-in user: {logged_in_user.username}")

    # If the logged-in user is a superuser and the selected user is different, create a notification for the selected user
    if logged_in_user.is_superuser and selected_user_username and selected_user_username != logged_in_user.username:
        try:
            selected_user = User.objects.get(username=selected_user_username)
            Notification.objects.create(
                user=selected_user,
                message=user_message,
            )
            print(f"Notification created for selected user: {selected_user.username}")
        except User.DoesNotExist:
            # Handle the case where the selected user does not exist
            print(f"User with username '{selected_user_username}' does not exist.")