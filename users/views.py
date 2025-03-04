from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, CustomAuthenticationForm
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.conf import settings
from django import forms
from .gcs_storage import upload_to_gcs
from .tokens import account_activation_token
from bs4 import BeautifulSoup
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.models import User

@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        #All newly created users should initially comes across as inactive, before their email is activated

        if user is not None:    
            try:
                # Confirm if the user is allowed to log in (check if they are active)
                form.confirm_login_allowed(user)
                login(request, user)  # If no error is raised, log the user in
                return redirect('landing_page')


            except forms.ValidationError as e:
                form.add_error(None, e)  # Add validation error to the form
                print("Added inactive account error")

        else:
            form.add_error(None, "Please activate your account via email before logging in")
        
    else:
        form = CustomAuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('landing_page')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False  # Deactivate account until email is confirmed
                user.save()
                current_site = get_current_site(request)
                mail_subject = 'Activate your account.'
                message = render_to_string('registration/email_verification.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                })
                to_email = form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.content_subtype = "html"  # Set the email content to HTML
                email.send()
                messages.success(request, f'Account created for {user.username}! Please confirm your email to complete the registration.')
                return redirect('login')
            except IntegrityError:
                form.add_error('username', 'Username already exists. Please choose a different username.')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        # login(request, user) Do not log in user automatically. Route them to login page
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
        return render(request, 'registration/activation_invalid.html')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            forms_saved = True

            try:
                user_form.save()
            except Exception as e:
                forms_saved = False
                print('Error saving UserUpdateForm:', e)

            try:
                profile_form.save()
            except Exception as e:
                forms_saved = False
                print('Error saving ProfileUpdateForm:', e)

            if forms_saved:
                messages.success(request, 'Your account has been updated!')
            return redirect('profile')
        else:
            print("Form is not valid:", user_form.errors, profile_form.errors)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': user_form,
        'p_form': profile_form
    }

    return render(request, 'users/profile.html', context)

@csrf_exempt
def custom_ckeditor_upload(request):
    """Handles CKEditor file uploads to Google Cloud Storage."""
    print("custom_ckeditor_upload view called")

    if not request.user.is_authenticated:
        print("Unauthorized upload attempt")
        return HttpResponse("Unauthorized", status=401)

    if request.method == 'POST' and request.FILES:
        upload = request.FILES['upload']
        file_path = f'uploads/{request.user.username}/{upload.name}'
        file_content = upload.read()
        
        # Upload to GCS using utility function
        file_url = upload_to_gcs(settings.GS_BUCKET_NAME, file_path, file_content, upload.content_type)
        
        # Extract image dimensions from the HTML
        width = request.POST.get('width', 'auto')
        height = request.POST.get('height', 'auto')
        
        return JsonResponse({'uploaded': 1, 'fileName': upload.name, 'url': file_url, 'width': width, 'height': height})

    return JsonResponse({'uploaded': 0, 'error': {'message': 'No file uploaded'}})

