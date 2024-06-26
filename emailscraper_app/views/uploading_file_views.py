from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from ..models import EmailFileUpload
from ..forms import EmailFileForm


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
