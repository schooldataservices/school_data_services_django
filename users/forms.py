from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from .widgets import CustomClearableFileInput

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists. Please choose a different username.')
        return username

class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=CustomClearableFileInput(attrs={'initial_text': 'Profile picture'}))

    class Meta:
        model = Profile
        fields = ['image']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if hasattr(image, 'content_type'):
                if not image.content_type.startswith('image'):
                    raise forms.ValidationError("File is not a valid image.")
        return image

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):

        print('Calling confirm login allowed')

        print(f"User info - Username: {user.username}, Email: {user.email}, Is Active: {user.is_active}, Last Login: {user.last_login}")



        # print(f"confirm_login_allowed called for user: {user.username}")
        if not user.is_active:
            print("User is inactive")
            raise forms.ValidationError(
                "Your account is inactive. Please check your email to activate your account.",
                code='inactive',
            )
        print("User is active")



