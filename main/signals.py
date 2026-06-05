# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application
from .utils import send_approval_email

@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, created, **kwargs):
    if created:
        return
    if instance.status == 'approved' and not instance.is_notified:
        send_approval_email(instance)
        Application.objects.filter(pk=instance.pk).update(is_notified=True)
        instance.is_notified = True