from django.contrib import admin
from .models import HomePage, Event, Service, Tariff, Application, Program

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'price', 'is_active')

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'category', 'event_date', 'event_time', 'tariff')
    list_filter = ('category', 'event_date', 'tariff')
    
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'type', 'image') 
    list_filter = ('category', 'type')
    search_fields = ('title', 'description')

admin.site.register(HomePage)
#admin.site.register(Service)