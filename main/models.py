from django.db import models

class HomePage(models.Model):
    welcome_text = models.CharField(max_length=255, verbose_name="Заголовок приветствия")
    subtitle = models.TextField(verbose_name="Подзаголовок/Описание")
    banner_image = models.ImageField(upload_to='home/', blank=True, null=True, verbose_name="Главный баннер")
    
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email для связи")
    address = models.CharField(max_length=500, blank=True, verbose_name="Адрес театра")

    def __str__(self):
        return "Настройки главной страницы и контактов"

    class Meta:
        verbose_name = "Главная страница и контакты"

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
        db_table = 'main_event'
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
    duration = models.CharField(max_length=100, verbose_name="Длительность")
    image = models.ImageField(upload_to='tariffs/', blank=True, null=True, verbose_name="Картинка тарифа")

    def __str__(self):
        return f"{self.get_category_display()} — {self.name} ({self.price} ₽)"

    class Meta:
        managed = True
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"
        db_table = 'tariff' 

class Application(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'День рождения'),
        ('graduation', 'Выпускной'),
        ('spectacle', 'Спектакль'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('processing', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Категория")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True, null=True)
    age = models.CharField(max_length=50, verbose_name="Возраст детей", blank=True, null=True)
    address = models.CharField(max_length=500, verbose_name="Адрес", blank=True, null=True)
    event_date = models.DateField(verbose_name="Дата события", null=True, blank=True)
    event_time = models.TimeField(verbose_name="Время события", null=True, blank=True)
    
    tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, verbose_name="Выбранный тариф", null=True, blank=True)
    
    chosen_show = models.ForeignKey("Program", on_delete=models.SET_NULL, verbose_name="Шоу-программа", null=True, blank=True, related_name="apps_show")
    chosen_program = models.ForeignKey("Program", on_delete=models.SET_NULL, verbose_name="Интерактивная программа", null=True, blank=True, related_name="apps_program")
    
    guests_count = models.PositiveIntegerField(verbose_name="Кол-во гостей", default=1, blank=True, null=True)
    message = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")

    def __str__(self):
        return f"{self.full_name} — {self.get_category_display()} ({self.status})"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        
class Program(models.Model):
    CATEGORY_CHOICES = [
        ('birthday', 'День рождения'),
        ('graduation', 'Выпускной'),
    ]
    TYPE_CHOICES = [
        ('show', 'Шоу-программа'),
        ('interactive', 'Интерактивная программа'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Для какой страницы")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Тип программы", null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Название программы")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='programs/', blank=True, null=True, verbose_name="Картинка программы")
    

    def __str__(self):
        return f"{self.get_category_display()} — {self.get_type_display()}: {self.title}"

    class Meta:
        managed = True
        db_table = 'main_program'
        verbose_name = "Программа"
        verbose_name_plural = "Программы"