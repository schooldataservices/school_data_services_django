from django.contrib import admin

from .models import Email, EmailMetadata, RequestConfig   # Replace with your actual model names

admin.site.register(Email)
admin.site.register(EmailMetadata)
admin.site.register(RequestConfig)  