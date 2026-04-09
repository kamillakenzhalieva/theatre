from django.contrib import admin
from .models import HomePage, Event, Service, Tariff, Application

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'service', 'price')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'category', 'event_date_time', 'tariff') 
    list_filter = ('category', 'event_date_time')

admin.site.register(HomePage)
admin.site.register(Event)