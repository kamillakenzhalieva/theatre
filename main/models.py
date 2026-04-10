from django.db import models

class HomePage(models.Model):
    welcome_text = models.CharField(max_length=255)
    subtitle = models.TextField()
    banner_image = models.ImageField(upload_to='home/', blank=True, null=True)

    def __str__(self):
        return "Контент главной страницы"

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название спектакля")
    
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание (для афиши)")
   
    description = models.TextField(verbose_name="Полное описание спектакля")
    date = models.DateTimeField(verbose_name="Дата и время начала")
    location = models.CharField(max_length=255, verbose_name="Локация (зал/адрес)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена билета")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Картинка/Постер")
    is_active = models.BooleanField(default=True, verbose_name="Отображать на сайте")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Спектакль/Мероприятие"
        verbose_name_plural = "Спектакли и мероприятия"

class Service(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'День рождения'),
        ('graduation', 'Выпускной'),
        ('spectacle', 'Спектакль'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.title}"

class Tariff(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='tariffs')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features_list = models.TextField(help_text="Список услуг через перенос строки")

    def __str__(self):
        return f"{self.service.title} — {self.name} ({self.price} ₽)"

class Application(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'День рождения'),
        ('graduation', 'Выпускной'),
        ('spectacle', 'Спектакль'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    age = models.CharField(max_length=50, verbose_name="Возраст детей")
    address = models.CharField(max_length=500)
    event_date_time = models.DateTimeField()
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name="Выбранный тариф")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.category} ({self.tariff.name})"