from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from google.cloud import storage
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
import pandas as pd
from io import StringIO



def serve_gcs_file(request, file_path, pandas_request = None):
    # Use default_storage to access files
    if not default_storage.exists(file_path):
        raise Http404("File not found")

    # Download file content
    file_content = default_storage.open(file_path).read()

    if pandas_request is not None:
        response = file_content.decode('utf-8')
        return(response)

    response = HttpResponse(file_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_path.split("/")[-1]}"'
    return(response)


def read_csv_from_gcs(request, file_path, pandas_request):
    try:
        # Get the content of the file
        file_content = serve_gcs_file(request, file_path, pandas_request)
        
        # Convert the string content to a file-like object
        file_like_object = StringIO(file_content)
        
        # Read CSV data from the file-like object
        df = pd.read_csv(file_like_object)
        
        # Now `df` is a DataFrame that you can work with
        print(df.head())  # Print the first few rows of the DataFrame for verification

        return df
    except FileNotFoundError as e:
        print(f'Error: {e}')
    except pd.errors.ParserError as e:
        print(f'Error parsing CSV: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')




