from django.core.exceptions import ValidationError
import re


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


def validate_unique_game_title():
    pass


def validate_unique_console_title():
    pass


def validate_file_size(size_mb=5):
    def validator(image):
        if image.size >= size_mb * 1048576:
            raise ValidationError(f'The maximum file size to upload is {size_mb}MB')
    return validator
