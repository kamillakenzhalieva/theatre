from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import HomePage, Event, Service, Tariff, Application
from .serializers import (
    HomePageSerializer, EventSerializer, ServiceSerializer, 
    TariffSerializer, ApplicationSerializer
)
import datetime
from django.http import JsonResponse

def index(request):
    home_data = HomePage.objects.first() 
    return render(request, 'index.html', {'home': home_data})

def about(request):
    home_data = HomePage.objects.first()
    return render(request, 'about.html', {'home': home_data})

def afisha(request):
    events = Event.objects.all()
    return render(request, 'afisha.html', {'events': events})

def spectacles_view(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    return render(request, 'spectacles.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})

def birthday_page(request):
    tariffs = Tariff.objects.filter(category='birthday')
    packages = [{
        'title': t.name,
        'price': t.price,
        'features': [f.strip() for f in t.features_list.split('\n') if f.strip()],
    } for t in tariffs]
    return render(request, 'birthdays.html', {'packages': packages})

def graduation_view(request):
    tariffs = Tariff.objects.filter(category='graduation')
    packages = [{
        'title': t.name,
        'price': t.price,
        'features': [f.strip() for f in t.features_list.split('\n') if f.strip()],
    } for t in tariffs]
    return render(request, 'graduation.html', {'packages': packages})

def admin_panel(request):
    return render(request, 'admin_panel.html')


class HomePageViewSet(viewsets.ModelViewSet):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class TariffViewSet(viewsets.ModelViewSet):
    queryset = Tariff.objects.all()
    serializer_class = TariffSerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        cat_map = {
            'День Рождения': 'birthday',
            'Выпускной': 'graduation',
            'Спектакль': 'spectacle'
        }
        
        if data.get('category') in cat_map:
            data['category'] = cat_map[data.get('category')]

        if 'selection' in data and not data.get('tariff'):
            tariff = Tariff.objects.filter(name=data.get('selection')).first()
            if tariff:
                data['tariff'] = tariff.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        if request.accepted_renderer.format == 'html':
            return redirect('home')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
def calendar_events_api(request):
    data = []

    for ev in Event.objects.filter(is_active=True):
        data.append({
            'id': f"ev_{ev.id}",
            'title': f"🎭 {ev.title}",
            'start': ev.date.isoformat(),
            'backgroundColor': '#a2d2ff', 
            'borderColor': '#7fb3e6',
            'extendedProps': {
                'description': ev.short_description,
                'location': ev.location
            }
        })


    apps = Application.objects.exclude(event_date__isnull=True).exclude(event_time__isnull=True)
    for ap in apps:
        start_dt = datetime.datetime.combine(ap.event_date, ap.event_time)
        
        is_bday = ap.category == 'birthday'
        color = '#ff8b94' if is_bday else '#a8e6cf'
        icon = '🎂' if is_bday else '🎓'

        data.append({
            'id': f"ap_{ap.id}",
            'title': f"{icon} {ap.full_name}",
            'start': start_dt.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'phone': ap.phone,
                'tariff': ap.tariff.name if ap.tariff else 'Не указан'
            }
        })

    return JsonResponse(data, safe=False)

def calendar_page_render(request):
    return render(request, 'calendar_view.html')