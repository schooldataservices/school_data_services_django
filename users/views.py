from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileUpdateForm, UserUpdateForm


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

    if request.method == 'POST':
        #pass in new post data
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES,
                                   instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request, f'Your account has been updated!')
            return redirect('profile') #redirect here because POST, GET, REDIRECT PATTERN
                                        #redirect causes a get request which prevents secondary post on reload
    else:
        #otherwise provide default
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    #variables that we are going to access within the template
    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)
