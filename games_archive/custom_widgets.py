from django.contrib.auth import get_user_model
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
                'image_url': console.default_image if console.default_image else None,
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


# Auxiliary function to generate stars icons for rating
def get_star_rating_html(rating):
    full_stars = int(rating)  # Number of solid stars
    half_star = 1 if rating - full_stars >= 0.5 else 0  # Determine if there's a half star
    empty_stars = 5 - full_stars - half_star  # The rest will be empty stars

    # Generate the HTML for the star rating
    stars_html = ''
    stars_html += '<i class="fas fa-star"></i>' * full_stars
    stars_html += '<i class="fas fa-star-half-alt"></i>' * half_star
    stars_html += '<i class="far fa-star"></i>' * empty_stars

    return stars_html


# auxiliary function to set default to_user in Games and Consoles models if user profile is deleted
def get_default_superuser():
    User = get_user_model()
    # Get the first superuser, if none exists return None
    superuser = User.objects.filter(is_superuser=True).first()
    staff = User.objects.filter(is_staff=True).first()
    if superuser:
        return superuser.pk
    elif staff:
        return staff.pk
    return User.objects.first().pk

