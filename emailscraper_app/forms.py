from django import forms
from .models import RequestConfig
from .email_setup import *
from ckeditor_uploader.widgets import CKEditorUploadingWidget



class RequestConfigForm(forms.ModelForm):
    class Meta:
        model = RequestConfig
        fields = ['priority_status', 'schedule_time', 'email_content', 'completion_status']

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





class EmailContentForm(forms.Form):
    email_content = forms.CharField(widget=CKEditorUploadingWidget(), label='Email Content')



