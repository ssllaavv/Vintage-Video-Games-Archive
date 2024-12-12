from django.contrib import admin
from django.contrib.sessions.models import Session
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import logout
from django.contrib.auth import get_user_model

from games_archive.accounts.models import GamesArchiveUser


def is_logged_in(user, request=None):
    """
    Check if user is logged in and display appropriate icon with logout link.
    Adds '(admin!)' text if the user is the current admin.
    """
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user.id) == str(data.get('_auth_user_id')):
            # User is logged in, show green icon with logout link
            logout_url = reverse('admin:logout_user', args=[user.id])
            # Check if this user is the current admin
            is_current_admin = request and request.user.id == user.id
            admin_text = " (admin!)" if is_current_admin else ""
            return format_html(
                '<img src="/static/admin/img/icon-yes.svg" alt="True"> '
                '<a href="{}" style="margin-left: 5px;">Logout</a>{}',
                logout_url,
                admin_text
            )
    # User is not logged in, show red icon
    return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')


# Make the function work with the request context
def make_is_logged_in(request):
    def login_status(user):
        return is_logged_in(user, request)

    return login_status


wrapped_is_logged_in = make_is_logged_in(None)  # Default wrapper with no request
wrapped_is_logged_in.short_description = 'Is Logged In'


@admin.register(GamesArchiveUser)
class GamesArchiveUserAdmin(admin.ModelAdmin):
    list_display = [
        'pk',
        'username',
        'last_name',
        'first_name',
        'email',
        'gender',
        'age',
        'is_staff',
        'is_superuser',
        wrapped_is_logged_in,  # Use the wrapped function
    ]
    search_fields = ['username', 'email', 'last_name']
    search_help_text = 'Search by: username, email, last name'
    list_filter = ['age', 'gender']
    ordering = ['-is_staff', 'pk']

    limited_fieldsets = (
        ('General', {'fields': (
            'username',
            'password',
            'date_joined',
            'last_login',
            'is_superuser',
            'is_staff',
            'is_active',
            # 'user_permissions',
            # 'groups',

        )}),
        ('Personal info', {'classes': ('collapse',), 'fields': (
            'first_name',
            'last_name',
            'email',
            'gender',
            'age',
            'profile_picture'
        )}),
    )

    # Keep the default UserAdmin fieldsets for superusers
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name='GOD USER').exists():
            return super().get_fieldsets(request, obj)
        return self.limited_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser or request.user.groups.filter(name='GOD USER').exists()

        if not is_superuser:
            # Disable certain fields for non-superusers
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'is_staff' in form.base_fields:
                form.base_fields['is_staff'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True
            if 'groups' in form.base_fields:
                form.base_fields['groups'].disabled = True

        return form

    def get_list_display(self, request):
        """
        Override get_list_display to inject the request into is_logged_in function
        """
        list_display = super().get_list_display(request)
        # Replace the wrapped_is_logged_in with a version that has access to request
        list_display = list(list_display)
        list_display[list_display.index(wrapped_is_logged_in)] = make_is_logged_in(request)
        return list_display

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('logout_user/<int:user_id>/',
                 self.admin_site.admin_view(self.logout_user),
                 name='logout_user'),
        ]
        return custom_urls + urls

    def logout_user(self, request, user_id):
        User = get_user_model()
        try:
            user_to_logout = User.objects.get(id=user_id)

            # Find and delete all sessions for this user
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            session_deleted = False

            for session in sessions:
                data = session.get_decoded()
                if str(user_id) == str(data.get('_auth_user_id')):
                    # Delete the session from the database
                    session.delete()
                    session_deleted = True

                    # If the logged-out user is the current user, properly log them out
                    if request.user.id == user_id:
                        logout(request)

            if session_deleted:
                messages.success(request, f'User {user_to_logout.username} has been logged out successfully.')
            else:
                messages.warning(request, f'User {user_to_logout.username} was not logged in.')

        except User.DoesNotExist:
            messages.error(request, f'User with ID {user_id} does not exist.')
        except Exception as e:
            messages.error(request, f'Error logging out user ID {user_id}: {e}')

        return HttpResponseRedirect(request. META.get('HTTP_REFERER', '/admin/'))

