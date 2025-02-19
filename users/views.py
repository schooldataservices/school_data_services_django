from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from ckeditor_uploader.views import upload

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('landing_page')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('landing_page')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        print("Raw form data:", request.POST)

        if form.is_valid():
            try:
                user = form.save()
                print(f"User created: {user.username}")
            except Exception as e:
                print(f"Error while saving user: {e}")
                return HttpResponse(f"Error: {e}", status=500)

            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
        else:
            print("Form is not valid:", form.errors)

    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)

@csrf_exempt
def custom_ckeditor_upload(request):
    print("custom_ckeditor_upload view called")
    if request.user.is_authenticated:
        print(f"Authenticated user: {request.user.username}")
        return upload(request)
    else:
        print("Unauthorized upload attempt")
        print(f"Request user: {request.user}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")
        return HttpResponse("Unauthorized", status=401)
