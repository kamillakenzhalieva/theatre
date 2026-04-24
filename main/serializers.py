from rest_framework import serializers
from .models import HomePage, Event, Service, Tariff, Application, EntertainmentItem

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


class EntertainmentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntertainmentItem
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    class Meta:
        model = Application
        fields = '__all__'