import re
from datetime import timedelta, datetime
from django.db import models
from django.core.exceptions import ValidationError
from django_better_admin_arrayfield.models.fields import ArrayField as BetterArrayField
from django.utils.timezone import make_aware, is_naive
from django.db.models.signals import post_save
from django.dispatch import receiver

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


class Staff(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="ФИО сотрудника")
    roles = BetterArrayField(
        models.CharField(max_length=100, blank=True),
        verbose_name="Роли",
        blank=True,
        default=list
    )

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

class StaffGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название группы")
    members = models.ManyToManyField(Staff, related_name='groups', verbose_name="Члены группы")

    def __str__(self):
        return self.name
    
class Event(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Краткое описание")
    description = models.TextField(verbose_name="Описание")
    date = models.DateTimeField(verbose_name="Дата и время")
    location = models.CharField(max_length=255, verbose_name="Локация")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='events/', blank=True, null=True, verbose_name="Постер")
    is_active = models.BooleanField(default=True, verbose_name="Отображать")
    assigned_group = models.ForeignKey(
        StaffGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Назначенная команда"
    )

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
        return f"{self.get_category_display()} — {self.name} ({int(self.price)} ₽)"

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
    assigned_group = models.ForeignKey(
        StaffGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Назначенная команда",
        related_name='applications'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    is_notified = models.BooleanField(default=False)
    
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


class Assignment(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Сотрудник")
    group = models.ForeignKey(StaffGroup, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Команда")
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Заявка")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Репертуарный спектакль")

    class Meta:
        verbose_name = "Назначение сотрудника"
        verbose_name_plural = "Назначения сотрудников"

    def __str__(self):
        target = self.application if self.application else self.event
        person = self.staff if self.staff else self.group
        return f"{person} -> {target}"

    @staticmethod
    def calculate_intervals(obj):
        if isinstance(obj, Application):
            if not obj.event_date or not obj.event_time:
                return None, None
            
            duration_minutes = 60
            if obj.category != 'spectacle' and obj.tariff and obj.tariff.duration:
                d_str = str(obj.tariff.duration).lower().strip()
                nums = re.findall(r'\d+', d_str)
                if nums:
                    val = int(nums[0])
                    duration_minutes = val if 'мин' in d_str else val * 60
            
            total_duration = duration_minutes + 60
            
            start_dt = datetime.combine(obj.event_date, obj.event_time)
            if is_naive(start_dt): start_dt = make_aware(start_dt)
            return start_dt, start_dt + timedelta(minutes=total_duration)

        elif isinstance(obj, Event):
            if not obj.date: return None, None
            start_dt = obj.date
            if is_naive(start_dt): start_dt = make_aware(start_dt)
            return start_dt, start_dt + timedelta(hours=2)
            
        return None, None

    def clean(self):
        super().clean()
        current_obj = self.application if self.application else self.event
        if not current_obj:
            raise ValidationError("Не выбрано мероприятие!")
        
        if self.staff_id:
            curr_start, curr_end = self.calculate_intervals(current_obj)
            if not curr_start: return

            others = Assignment.objects.filter(
                models.Q(staff_id=self.staff_id) | models.Q(group__members__id=self.staff_id)
            ).exclude(pk=self.pk).distinct()

            for other in others:
                other_obj = other.application if other.application else other.event
                if not other_obj: continue
                o_start, o_end = self.calculate_intervals(other_obj)
                if o_start and o_end and (curr_start < o_end and curr_end > o_start):
                    raise ValidationError(f"Сотрудник {self.staff.full_name} жестко занят на другом мероприятии!")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

@receiver(post_save, sender=Assignment)
def update_assigned_group(sender, instance, **kwargs):
    if instance.event:
        Event.objects.filter(id=instance.event.id).update(assigned_group=instance.group)
    if instance.application:
        Application.objects.filter(id=instance.application.id).update(assigned_group=instance.group)