from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import HomePage, Event, Service, Tariff, Application, Program, Assignment, Staff, StaffGroup
from .serializers import (
    HomePageSerializer, EventSerializer, ServiceSerializer, 
    TariffSerializer, ApplicationSerializer, AssignmentSerializer, StaffSerializer, StaffGroupSerializer
)
import datetime
import re
from django.http import JsonResponse
from datetime import timedelta

def index(request):
    home_data = HomePage.objects.first() 
    return render(request, 'main/index.html', {'home': home_data})

def about(request):
    home_data = HomePage.objects.first()
    return render(request, 'main/about.html', {'home': home_data})

def afisha(request):
    events = Event.objects.all()
    return render(request, 'main/afisha.html', {'events': events})

def spectacles_view(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    return render(request, 'main/spectacles.html', {'events': events})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'main/event_detail.html', {'event': event})

def birthday_page(request):
    tariffs = Tariff.objects.filter(category='birthday')
    shows = Program.objects.filter(category='birthday', type='show')
    interactives = Program.objects.filter(category='birthday', type='interactive')
    all_shows = Program.objects.filter(type='show')
    all_interactives = Program.objects.filter(type='interactive')
    spectacles = Event.objects.filter(is_active=True)
    all_tariffs = Tariff.objects.all()
    return render(request, 'main/birthdays.html', {
        'tariffs': tariffs,
        'all_tariffs': all_tariffs,
        'shows': shows,
        'interactives': interactives,
        'all_shows': all_shows,
        'all_interactives': all_interactives,
        'spectacles': spectacles
    })

def graduation_view(request):
    tariffs = Tariff.objects.filter(category='graduation')
    shows = Program.objects.filter(category='graduation', type='show')
    interactives = Program.objects.filter(category='graduation', type='interactive')
    all_shows = Program.objects.filter(type='show')
    all_interactives = Program.objects.filter(type='interactive')
    spectacles = Event.objects.filter(is_active=True)
    all_tariffs = Tariff.objects.all()
    return render(request, 'main/graduation.html', {
        'tariffs': tariffs,
        'all_tariffs': all_tariffs,
        'shows': shows,
        'interactives': interactives,
        'all_shows': all_shows,
        'all_interactives': all_interactives,
        'spectacles': spectacles
    })

def admin_panel(request):
    return render(request, 'main/admin_panel.html')

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
        raw_category = data.get('category')
        if raw_category in cat_map:
            data['category'] = cat_map[raw_category]

        tariff_val = data.get('tariff')
        if tariff_val and not str(tariff_val).isdigit():
            tariff_obj = Tariff.objects.filter(name=tariff_val).first()
            data['tariff'] = tariff_obj.id if tariff_obj else None

        for field in ['chosen_show', 'chosen_program']:
            val = data.get(field)
            if val and not str(val).isdigit():
                prog = Program.objects.filter(title=val).first()
                data[field] = prog.id if prog else None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def calendar_events_api(request):
    data = []
    for ev in Event.objects.filter(is_active=True):
        data.append({
            'id': ev.id,
            'title': f"🎭 {ev.title}",
            'start': ev.date.isoformat(),
            'backgroundColor': '#a2d2ff', 
            'borderColor': '#7fb3e6',
            'extendedProps': {
                'type': 'event',
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
            'id': ap.id,
            'title': f"{icon} {ap.full_name}",
            'start': start_dt.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'type': 'application',
                'phone': ap.phone,
                'tariff': ap.tariff.name if ap.tariff else 'Не указан'
            }
        })
    return JsonResponse(data, safe=False)

def calendar_page_render(request):
    return render(request, 'main/calendar_view.html')

def get_service_data(request):
    category_map = {
        'День Рождения': 'birthday',
        'Выпускной': 'graduation',
        'Спектакль': 'spectacle'
    }
    category_label = request.GET.get('category')
    category = category_map.get(category_label)

    if category_label == 'Спектакль':
        items = list(Event.objects.filter(is_active=True).values_list('title', flat=True))
        return JsonResponse({'tariffs': items, 'shows': [], 'interactives': []})
    
    if category:
        tariffs = list(Tariff.objects.filter(category=category).values_list('name', flat=True))
        shows = list(Program.objects.filter(category=category, type='show').values_list('title', flat=True))
        interactives = list(Program.objects.filter(category=category, type='interactive').values_list('title', flat=True))
        return JsonResponse({
            'tariffs': tariffs,
            'shows': shows,
            'interactives': interactives
        })
    return JsonResponse({'error': 'Invalid category'}, status=400)

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if request.data.get('dry_run'):
            return Response({"status": "available"}, status=status.HTTP_200_OK)
            
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StaffGroupViewSet(viewsets.ModelViewSet):
    queryset = StaffGroup.objects.all()
    serializer_class = StaffGroupSerializer