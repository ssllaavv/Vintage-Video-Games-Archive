# from django.db.models import ImageField
# from PIL import Image
# from io import BytesIO
# from django.core.files.base import ContentFile
#
#
# class ResizableImageField(ImageField):
#     def __init__(self, max_file_size, *args, **kwargs):
#         self.max_file_size = max_file_size  # Max file size in bytes
#         super().__init__(*args, **kwargs)
#
#     def pre_save(self, model_instance, add):
#         image_field = getattr(model_instance, self.attname)
#         if image_field:
#             img = Image.open(image_field)
#             img_format = img.format  # Get the image format (e.g., JPEG, PNG)
#             img_io = BytesIO()
#
#             # If the image is already below the max size, save it as is
#             if image_field.size <= self.max_file_size:
#                 img_io.seek(0)
#                 img.save(img_io, format=img_format)
#                 img_content = ContentFile(img_io.getvalue())
#                 image_field.save(image_field.name, img_content, save=False)
#                 return image_field
#
#             # Resize and compress the image
#             img = self._resize_and_compress_image(img, img_io, img_format)
#
#             # Save the resized image back to the image field
#             im g_content = ContentFile(img_io.getvalue())
#             image_field.save(f"{model_instance.pk}_resized.{img_format.lower()}", img_content, save=False)
#         return image_field
#
#     def _resize_and_compress_image(self, img, img_io, img_format):
#         # Start with high quality
#         quality = 95
#         img_io.seek(0)  # Reset the buffer
#
#         # Resize if necessary and compress
#         while True:
#             img_io.seek(0)  # Reset the buffer
#             img.save(img_io, format=img_format, quality=quality)
#             file_size = img_io.tell()  # Get the file size in bytes
#
#             if file_size <= self.max_file_size:
#                 break  # Stop if the file is within the limit
#
#             # If file size is too large, reduce quality
#             quality -= 5  # Reduce quality
#
#             # If quality is too low, resize dimensions instead
#             if quality <= 10:
#                 img.thumbnail((img.width * 0.9, img.height * 0.9), Image.LANCZOS)  # Resize dimensions
#                 quality = 95  # Reset quality for the next round
#
#         return img
#
#     def deconstruct(self):
#         name, path, args, kwargs = super().deconstruct()
#         kwargs['max_file_size'] = self.max_file_size  # Add max_file_size to kwargs
#         return name, path, args, kwargs
