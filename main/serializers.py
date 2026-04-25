from rest_framework import serializers
from .models import HomePage, Event, Service, Tariff, Application, EntertainmentItem

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'
        extra_kwargs = {
            'subtitle': {'required': False, 'allow_blank': True}
        }

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

class EntertainmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntertainmentItem
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    entertainment_title = serializers.ReadOnlyField(source='entertainment.title')

    class Meta:
        model = Application
        fields = '__all__'
        extra_kwargs = {
            'full_name': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
            'email': {'required': False, 'allow_blank': True, 'allow_null': True},
            'age': {'required': False, 'allow_blank': True, 'allow_null': True},
            'address': {'required': False, 'allow_blank': True, 'allow_null': True},
            'event_date': {'required': False, 'allow_null': True},
            'event_time': {'required': False, 'allow_null': True},
            'guests_count': {'required': False, 'allow_null': True},
            'tariff': {'required': False, 'allow_null': True},
            'entertainment': {'required': False, 'allow_null': True},
            'message': {'required': False, 'allow_blank': True, 'allow_null': True},
            'status': {'required': False}
        }