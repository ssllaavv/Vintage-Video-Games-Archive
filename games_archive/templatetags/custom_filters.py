from django import template
from zoneinfo import ZoneInfo

register = template.Library()


@register.filter
def placeholder(value, token):
    value.field.widget.attrs['placeholder'] = token
    return value


@register.filter
def local_time(value, user_time_zone='UTC'):
    try:
        user_tz = ZoneInfo(user_time_zone)
        localized_time = value.astimezone(user_tz)
        return localized_time.strftime('%b. %d, %Y, %I:%M %p')
    except Exception:
        return value
