from django.forms.widgets import ClearableFileInput
from django.utils.safestring import mark_safe

class CustomClearableFileInput(ClearableFileInput):
    template_name = 'users/custom_clearable_file_input.html'

    def format_value(self, value):
        if self.is_initial(value):
            # print(f"Initial value: {value}")
            if hasattr(value, 'url'):
                print(f"URL: {value.url}")
                return mark_safe(f'<a href="{value.url}">Profile picture</a>')
            else:
                print("Value does not have a 'url' attribute.")
        return super().format_value(value)
