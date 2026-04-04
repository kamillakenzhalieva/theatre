from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название спектакля")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=150, verbose_name="Зал/Место")
    description = models.TextField(verbose_name="Описание")
    price = models.IntegerField(verbose_name="Минимальная цена (в рублях)")
    image = models.ImageField(upload_to='events_images/', verbose_name="Обложка/Афиша")
    ticket_link = models.URLField(verbose_name="Ссылка на покупку", blank=True, null=True)

    class Meta:
        verbose_name = "Спектакль"
        verbose_name_plural = "Спектакли"
        ordering = ['date']  

    def __str__(self):
        return self.title