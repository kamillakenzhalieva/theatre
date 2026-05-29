from django.core.mail import send_mail
from django.conf import settings
from .models import HomePage

def send_approval_email(application):
    home_settings = HomePage.objects.first()
    from_email = home_settings.email if (home_settings and home_settings.email) else settings.DEFAULT_FROM_EMAIL

    subject = 'Ваша заявка одобрена!'
    message = (
        f"Здравствуйте, {application.full_name}!\n\n"
        f"Отличные новости! Ваша заявка успешно одобрена!\n\n"
        f"Детали вашего бронирования:\n"
        f"📅 Дата: {application.event_date}\n"
        f"⏰ Время: {application.event_time}\n"
        f"📍 Адрес: {application.address}\n\n"
        f"Если у вас возникнут вопросы или планы изменятся, пожалуйста, свяжитесь с нами.\n\n"
        f"С уважением,\n"
        f'Команда театра "Новый стиль"!'
    )
    
    if application.email:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[application.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки почты: {e}")