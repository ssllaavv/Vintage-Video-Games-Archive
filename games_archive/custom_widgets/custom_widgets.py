from django.forms.widgets import SelectMultiple
from django.forms.widgets import ClearableFileInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class ConsoleSelectMultiple(SelectMultiple):
    template_name = "partials/console_select.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Get all available consoles
        from games_archive.consoles.models import Console
        consoles = Console.objects.all()

        # Prepare options with additional data
        options = []
        selected_values = set(value) if value else set()

        for console in consoles:
            options.append({
                'id': console.id,
                'name': console.name,
                'image_url': console.cover_image.url if console.cover_image else None,
                'selected': str(console.id) in selected_values or console.id in selected_values
            })

        context['widget']['options'] = options
        return context

    def render(self, name, value, attrs=None, renderer=None):
        context = self.get_context(name, value, attrs)
        return mark_safe(render_to_string(self.template_name, context))


class CustomImageUploadWidget(ClearableFileInput):
    template_name = 'partials/custom_image_upload.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'is_image_field': True,
            'has_image': bool(value and hasattr(value, 'url')),
            'image_url': value.url if value and hasattr(value, 'url') else None,
        })
        return context

