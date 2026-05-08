from rest_framework import serializers
from .models import HomePage, Event, Service, Tariff, Application, Program

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    show_name = serializers.ReadOnlyField(source='chosen_show.title')
    program_name = serializers.ReadOnlyField(source='chosen_program.title')

    class Meta:
        model = Application
        fields = [
            'id', 'category', 'full_name', 'phone', 'email', 
            'age', 'address', 'event_date', 'event_time', 
            'tariff', 'tariff_name', 
            'chosen_show', 'show_name',
            'chosen_program', 'program_name',
            'guests_count', 'message', 'status', 'created_at'
        ]

    def validate_tariff(self, value):
        return value if value != "" else None

    def validate_chosen_show(self, value):
        return value if value != "" else None

    def validate_chosen_program(self, value):
        return value if value != "" else None