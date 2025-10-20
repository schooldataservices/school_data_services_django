from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from datetime import datetime
from django.http import JsonResponse
from ..models import RequestConfig, Notification 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def landing_page(request):
    return render(request, 'sds_app/landing_page.html')

def problem_solution(request):
    return render(request, 'sds_app/challenges_faced.html')

def data_modeling(request):
    return render(request, 'sds_app/data_modeling.html')

def data_pipelines(request):
    return render(request, 'sds_app/data_pipelines.html')

def cloud_setup(request):
    return render(request, 'sds_app/cloud_setup.html')



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

def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        # print(f"Notifications fetched: {notifications}")
        notifications_data = [
            {
                'id': notification.id,
                'message': notification.message,
                'timestamp': notification.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for notification in notifications
        ]
        return JsonResponse({'notifications': notifications_data})
    return JsonResponse({'error': 'Unauthorized'}, status=401)



@csrf_exempt
def mark_notifications_as_read(request):
    if request.user.is_authenticated and request.method == 'POST':
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        # print(f"Marking notifications as read: {unread_notifications}")
        unread_notifications.update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Unauthorized'}, status=401)