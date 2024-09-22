from django.core.exceptions import ValidationError
import re


def validate_name(value):
    # Check if the name is at least 2 characters long
    if len(value) < 2:
        raise ValidationError('Name must be at least 2 characters long.')

    # Check if the name contains only letters (a-z, A-Z)
    if not re.match(r'^[A-Za-z]+$', value):
        raise ValidationError('Name must contain only letters.')

