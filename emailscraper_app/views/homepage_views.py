from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from google.cloud import storage
from datetime import datetime
from config import *


 
 

def landing_page(request):
    return render(request, 'emailscraper_app/landing_page.html')



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

