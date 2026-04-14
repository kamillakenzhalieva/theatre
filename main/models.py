from django.db import models

class HomePage(models.Model):
    welcome_text = models.CharField(max_length=255)
    subtitle = models.TextField()
    banner_image = models.ImageField(upload_to='home/', blank=True, null=True)

    def __str__(self):
        return "Контент главной страницы"

class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=255, verbose_name="Локация")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Постер")
    is_active = models.BooleanField(default=True, verbose_name="Отображать")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"

class Service(models.Model):
    title = models.CharField(max_length=200)
    
    def __str__(self):
        return self.title

class Tariff(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'День рождения'),
        ('graduation', 'Выпускной'),
        ('spectacle', 'Спектакль'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    features_list = models.TextField(verbose_name="Список услуг")

    def __str__(self):
        return f"{self.get_category_display()} — {self.name} ({self.price} ₽)"

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
    event_date = models.DateField(verbose_name="Дата события", null=True, blank=True)
    event_time = models.TimeField(verbose_name="Время события", null=True, blank=True)
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE, verbose_name="Выбранный тариф")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} — {self.get_category_display()} ({self.tariff.name})"