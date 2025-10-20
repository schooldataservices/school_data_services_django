from django import forms
from .models import RequestConfig
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class RequestConfigForm(forms.ModelForm):

    priority_status = forms.ChoiceField(
        choices=RequestConfig.PRIORITY_CHOICES,  # Ensure this matches your model choices
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        error_messages={'required': 'Priority status is required.'}
    )

    schedule_time = forms.DateTimeField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'datetimepicker form-control', 'placeholder': 'Select a date'}),
        error_messages={'required': 'Select the desired completion date.'}
    )

    email_content = forms.CharField(
        widget=CKEditorUploadingWidget(),
        label='Email Content',
        required=True,
        initial='',
        error_messages={'required': 'Email content is required.'}
    )

    request_title = forms.CharField(
        max_length=150,
        label="Request Title",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter a short title'}),
        required=True,
        error_messages={'required': 'Request title is required.'}
    )

    class Meta:
        model = RequestConfig
        fields = ['request_title', 'priority_status', 'schedule_time', 'email_content', 'completion_status']



