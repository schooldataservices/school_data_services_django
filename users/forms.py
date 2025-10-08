from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from .widgets import CustomClearableFileInput
from captcha.fields import ReCaptchaField

SCHOOL_CHOICES = [('', 'Select School')] + list(Profile._meta.get_field('school_acronym').choices)

class UserRegisterForm(UserCreationForm):
    captcha = ReCaptchaField(error_messages={'required': 'Please complete the CAPTCHA to register.'})
    email = forms.EmailField(required=True)
    school_acronym = forms.ChoiceField(
        choices=SCHOOL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'school_acronym', 'password1', 'password2', 'captcha']

    def clean_school_acronym(self):
        val = self.cleaned_data.get('school_acronym', '').strip()
        if not val:
            raise forms.ValidationError("Please select a school acronym.")
        return val

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
    school_acronym = forms.ChoiceField(
        choices=SCHOOL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Profile
        fields = ['image', 'school_acronym']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'content_type') and not image.content_type.startswith('image'):
            raise forms.ValidationError("File is not a valid image.")
        return image

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Your account is inactive. Please check your email to activate your account.",
                code='inactive',
            )



