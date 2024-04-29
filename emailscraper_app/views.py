from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import (ListView, 
                                  DetailView, 
                                  CreateView,
                                  UpdateView,
                                  DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.files.storage import FileSystemStorage
from django.urls import reverse_lazy
from .forms import EmailBlastForm, EmailConfigForm, EmailFileForm
from .models import EmailOption, EmailFileUpload
from users.models import Profile


import csv
from config import *
import pandas as pd
import codecs
import csv
import base64
from datetime import datetime
from emailscraper_app.modules.Sending_Emails import KC_schools
from email_send_main import blast

df = KC_schools.read_in()
df = KC_schools.filter_emails_by_sport(df, ['Baseball', 'Softball'])



# views are Python functions or classes that receive HTTP requests and return HTTP responses.
# Views contain the business logic of your application, including data retrieval, processing, and rendering.
# Views interact with MODELS to retrieve or manipulate data and with templates to generate HTML output.



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import EmailConfigForm
from .models import EmailOption
from users.models import Profile

@login_required
def email_config_view(request):
    excluded_fields = ['EMAIL_PASS', 'db_pass', 'db_user', 'table_name', 'server', 'database']

    form = request.session.get('email_config', {})

    if form == {}:
        form = EmailConfigForm()
    else:
        #take the dictionary from the session to make a form
        form = EmailConfigForm(form)

    if request.method == 'POST':

        form = EmailConfigForm(request.POST)
        if form.is_valid():
            filter_date = form.cleaned_data['filter_date'].strftime('%Y-%m-%d')
            form.cleaned_data['filter_date'] = filter_date

            request.session['email_config'] = form.cleaned_data
            messages.success(request, 'Email configuration saved successfully.')

            return redirect('email_config_home')
            
        else:
            print('Form is invalid')
            print(form.errors)
         
    else:
        print('Not a post request creating basic config form')

    for field_name in excluded_fields:
        if field_name in form.fields:
            del form.fields[field_name]

    emails = EmailOption.objects.all()
    profile_name = request.user.profile.user.username if hasattr(request.user, 'profile') else None
    first_time_login = request.user.last_login is None
    welcome_message = f'Welcome to the party, {request.user.username}!' if first_time_login else f'Welcome back, {profile_name}!'

    emails_sent = request.session.get('emails_sent', False)
    context = {
        'emails': emails,
        'welcome_message': welcome_message,
    }

    return render(request, 'emailscraper_app/homepage_base.html', {
        'email_config_form': form,
        'emails_sent': emails_sent,
        'email_context': context,
    })



def send_emails_view(request):

    email_config = request.session.get('email_config') #get the variables from the session, if saved it will be overwritten
    print('Send emails view has been called')

    if request.method == 'POST':

        for key, value in EmailConfigForm.excluded_fields.items():
            email_config[key] = value

        print(email_config)

        # Call the blast function from email_send_main.py, df can be configured to be passed in dynamically with the adlibs
        #currently reads df from views file being a global variable
        blast(email_config, df, test=True)

        messages.success(request, 'Emails sent successfully!')
        
        # Redirect to the homepage URL
        return redirect('email_config_home')
    
    else: #on initial page load
        form = EmailBlastForm()
        
    return render(request, 'emailscraper_app/homepage_base.html', {'form': form})


def file_list(request):

    if request.method == 'POST':
        form = EmailFileUploadForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = EmailFileUploadForm()

    context = {
        'files' : EmailFileUpload.objects.all(),
        'form': form
    }
    return render(request, 'emailscraper_app/file_list.html', context)


def upload_image_text_box(request):
    # Your existing code to initialize the form
    email_config_form = EmailConfigForm()

    # Check if the 'email_content' field should use CKEditor widget
    use_ckeditor = True  # Determine this based on your conditions

    return render(request, 'emailscraper_app/upload_image_text_box.html', {
        'email_config_form': email_config_form,
        'use_ckeditor': use_ckeditor,  # Pass the flag to the template
    })
















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
    # fields = ['file', 'file_tag']
    success_url = reverse_lazy('email-create')

    def form_valid(self, form):

        form.instance.creator_id = self.request.user
        response =  super().form_valid(form)
        messages.success(self. request, 'File has been uploaded successfully')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add all prior files submitted by the logged-in user to the context
        context['previous_files'] = EmailFileUpload.objects.filter(creator_id=self.request.user)
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
  

 

