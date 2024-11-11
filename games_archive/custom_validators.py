from django.core.exceptions import ValidationError
import re
from datetime import datetime


def validate_name_is_longer_than_2_characters(value):
    # Check if the name is at least 2 characters long
    if len(value) < 2:
        raise ValidationError('Name must be at least 2 characters long.')


def validate_name_contains_only_letters(value):
    # Check if the name contains only letters (a-z, A-Z)
    if not re.match(r'^[A-Za-z]+$', value):
        raise ValidationError('Name must contain only letters.')


def validate_name(value):
    validate_name_contains_only_letters(value)
    validate_name_is_longer_than_2_characters(value)


def validate_file_size(value):
    if value.size >= 5 * 1024 * 1024:
        raise ValidationError('The maximum file size to upload is 5MB')


def validate_year_less_than_current_year(value):
    current_year = datetime.now().year
    if value > current_year:
        raise ValidationError(f'The year {value} is later than the current year ({current_year}).')


def validate_year_more_than_1940r(value):
    if value < 1940:
        raise ValidationError('Please, enter year after 1940.')


def validate_release_year(value):
    validate_year_more_than_1940r(value)
    validate_year_less_than_current_year(value)
