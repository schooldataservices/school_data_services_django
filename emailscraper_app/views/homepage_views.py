from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from datetime import datetime
# from config import *


 
 

def landing_page(request):
    return render(request, 'emailscraper_app/landing_page.html')

def problem_solution(request):
    return render(request, 'emailscraper_app/challenges_faced.html')

def data_modeling(request):
    return render(request, 'emailscraper_app/data_modeling.html')

def data_pipelines(request):
    return render(request, 'emailscraper_app/data_pipelines.html')

def cloud_setup(request):
    return render(request, 'emailscraper_app/cloud_setup.html')


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

