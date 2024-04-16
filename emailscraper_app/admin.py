from django.contrib import admin
from .models import EmailFileUpload, EmailOption


# Register your models here in order to appear on admin site

admin.site.register(EmailFileUpload)
admin.site.register(EmailOption)
