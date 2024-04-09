from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm


def register(request):

    if request.method == 'POST':
        form = UserRegisterForm(request.POST) #If post, pass in user instantiated data
        #to add fields to this form, must create new form that inherits from UserCreationForm

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username') #form.cleaned_data is a dictionary
            messages.success(request, f'{username}, your account has been created, and you are now able to log in') #fill out a form and redirect to a new page
            return redirect('login')
    
    else:
        form = UserRegisterForm() #creating a blank form and registering it to the template

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):

    return render(request, 'users/profile.html')
