from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from games_archive import settings


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def send_greeting_email(sender, instance, created, **kwargs):
    if created:

        print("Sending email.... ")

        subject = "Registration greetings"
        html_message = render_to_string('email-greeting.html', {'user': instance})
        plain_message = strip_tags(html_message)
        to = instance.email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to, ],
            html_message=html_message
        )


