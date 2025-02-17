from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'users/widgets/custom_clearable_file_input.html'

    def format_value(self, value):
        if self.is_initial(value):
            return mark_safe(f'<a href="{value.url}">Profile pic link</a>')
        return super().format_value(value)
