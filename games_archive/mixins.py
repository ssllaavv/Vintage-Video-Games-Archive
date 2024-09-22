from django.db import models
from PIL import Image
import io


class ResizeImageMixin:
    MAX_IMAGE_FILE_SIZE = 5 * 1024 * 1024  # 5MB default max size

    def resize_image_if_necessary(self, image_field):
        # Open the uploaded image
        img = Image.open(image_field)
        img_format = img.format  # Get the original image format (JPEG, PNG, etc.)

        # Check if the image exceeds the max size
        img_io = io.BytesIO()
        img.save(img_io, format=img_format)
        size_in_bytes = img_io.tell()

        # Resize the image if it exceeds MAX_IMAGE_FILE_SIZE
        if size_in_bytes > self.MAX_IMAGE_FILE_SIZE:
            # Calculate the resize ratio
            ratio = (self.MAX_IMAGE_FILE_SIZE / size_in_bytes) ** 0.5

            # Resize the image while maintaining aspect ratio
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save the resized image to an in-memory file
            img_io = io.BytesIO()
            img.save(img_io, format=img_format, quality=85)  # Adjust quality if needed
            img_io.seek(0)

            # Update the image field with the resized image
            image_field.file = img_io
            image_field.size = img_io.tell()

        return image_field

    def save(self, *args, **kwargs):
        # Loop through all fields of the model (using self._meta.fields)
        for field in self._meta.get_fields():
            # Only operate on ImageFields
            if isinstance(field, models.ImageField):
                image_field = getattr(self, field.name)
                if image_field:
                    setattr(self, field.name, self.resize_image_if_necessary(image_field))

        # Call the original save method from the model class
        # We call the parent model's save method here, not the mixin's
        super(self.__class__, self).save(*args, **kwargs)
