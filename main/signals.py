from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application
from .utils import send_approval_email

@receiver(post_save, sender=Application)
def application_status_changed(sender, instance, created, **kwargs):
    if created:
        return
    
    # Отправляем только если статус 'approved' и мы еще не отправляли уведомление
    if instance.status == 'approved' and not instance.is_notified:
        send_approval_email(instance)
        # Ставим флаг, чтобы письмо не отправлялось повторно
        instance.is_notified = True
        instance.save(update_fields=['is_notified'])