from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from ..models import EmailFileUpload
from ..forms import EmailFileForm
from google.cloud import storage
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from django.conf import settings
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





#Somehow read in the file based on area, and provide attributes in dropdowns
class EmailListView(ListView): 

    model = EmailFileUpload
    template_name = 'emailscraper_app/homepage_base.html'
    context_object_name = 'file'
    #newest to oldest on files


class EmailDetailView(DetailView):  #form looks to model_detail.html by default
    model = EmailFileUpload



class EmailCreateView(LoginRequiredMixin, CreateView):  #looks to model_form.html by default

    model = EmailFileUpload
    form_class = EmailFileForm
    success_url = reverse_lazy('import-file')

    def form_valid(self, form):

        form.instance.creator_id = self.request.user
        response =  super().form_valid(form)
        messages.success(self. request, 'File has been uploaded successfully')
        return response
    
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # Get all files uploaded by the logged-in user
        previous_files = EmailFileUpload.objects.filter(creator_id=self.request.user)
        
        # Generate the file path for each file
        for file in previous_files:
            file.file_path = file.file.name  # Use the file's name as the path
        
        context['previous_files'] = previous_files
        return context
    

class EmailUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView): 

    model = EmailFileUpload
    fields = ['file', 'file_tag']

    def form_valid(self, form):  #ensure the form being submitted is by the user logged in
        form.instance.creator_id = self.request.user
        return super().form_valid(form)

    def test_func(self): #sees if user passes test condition when altering email confirming they initially posted

        email = self.get_object()
        if self.request.user == email.creator_id:
            return True
        else:
            return False
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all prior files submitted by the logged-in user to the context
        context['previous_files'] = EmailFileUpload.objects.filter(creator_id=self.request.user)
        #To Change the Header
        context['is_update_view'] = True
        return context


class EmailDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  #form looks to model_confirm_delete.html by default
    model = EmailFileUpload
    success_url = '/'
    #could put message saying succesfully deleted
    
    def test_func(self): #sees if user passes test condition when altering email confirming they initially posted

        email = self.get_object()
        if self.request.user == email.creator_id:
            return True
        else:
            return False
        
    def form_valid(self, form):
        """
        Override the delete method to display a success message.
        """
        messages.success(self.request, "Email successfully deleted.")
        return super().form_valid(form)
