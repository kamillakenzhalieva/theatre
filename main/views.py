from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import HomePage, Event, Service, Tariff, Application, Program, Assignment, Staff, StaffGroup
from .serializers import (
    HomePageSerializer, EventSerializer, ServiceSerializer, 
    TariffSerializer, ApplicationSerializer, AssignmentSerializer, StaffSerializer, StaffGroupSerializer, ProgramSerializer
)
from rest_framework.decorators import action
from django.db.models import Q  
import re
from django.http import JsonResponse
from datetime import datetime, timedelta 
from django.core.exceptions import ValidationError 
from django.db import transaction


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
        cat_map = {'День Рождения': 'birthday', 'Выпускной': 'graduation', 'Спектакль': 'spectacle'}
        raw_cat = data.get('category')
        if raw_cat in cat_map:
            data['category'] = cat_map[raw_cat]
        tariff_obj = None
        show_obj = None
        program_obj = None

        if data.get('category') == 'spectacle':
            spec_name = data.get('tariff')
            if spec_name:
                old_msg = data.get('message', '')
                data['message'] = f"Выбран спектакль: {spec_name}. {old_msg}"
            data['tariff'] = None
            data['chosen_show'] = None
            data['chosen_program'] = None
        else:

            category = data.get('category')
            tariff_name = data.get('tariff')
            if tariff_name and isinstance(tariff_name, str):
                tariff_obj = Tariff.objects.filter(category=category, name=tariff_name.strip()).first()
                data['tariff'] = tariff_obj.id if tariff_obj else None

            show_title = data.get('chosen_show')
            if show_title and isinstance(show_title, str):
                show_obj = Program.objects.filter(category=category, type='show', title=show_title.strip()).first()
                data['chosen_show'] = show_obj.id if show_obj else None

            program_title = data.get('chosen_program')
            if program_title and isinstance(program_title, str):
                program_obj = Program.objects.filter(category=category, type='interactive', title=program_title.strip()).first()
                data['chosen_program'] = program_obj.id if program_obj else None

        serializer = self.get_serializer(data=data)
        
        if not serializer.is_valid():
            error_msg = str(list(serializer.errors.values())[0][0])
            error_msg = re.sub(r"ErrorDetail\(string='(.*?)', code='.*?'\)", r"\1", error_msg)
            return Response({'status': 'warning', 'message': error_msg}, status=status.HTTP_200_OK)

        if request.data.get('dry_run'):
            return Response({"status": "available"}, status=status.HTTP_200_OK)
        instance = serializer.save(
            tariff=tariff_obj if data.get('category') != 'spectacle' else None,
            chosen_show=show_obj,
            chosen_program=program_obj
        )

        group_id = request.data.get('group')
        event_id = request.data.get('event')

        if event_id and group_id:
            from .models import Event
            # Event.objects.filter(id=event_id).update(assigned_group_id=group_id)

        response_data = serializer.data
        response_data['tariff'] = instance.tariff.name if instance.tariff else (spec_name if data.get('category') == 'spectacle' else None)
        response_data['chosen_show'] = instance.chosen_show.title if instance.chosen_show else None
        response_data['chosen_program'] = instance.chosen_program.title if instance.chosen_program else None

        return Response(response_data, status=status.HTTP_201_CREATED)
    
def calendar_events_api(request):
    data = []
    for ev in Event.objects.filter(is_active=True):
        assign = Assignment.objects.filter(event=ev).first()
        
        if assign:
            if assign.group:
                who = f" — [{assign.group.name}]"
            elif assign.staff:
                who = f" — [{assign.staff.full_name}]"
            else:
                who = " — [Не назначен]"
        else:
            who = ""
        
        data.append({
            'id': f"ev{ev.id}",
            'title': f"🎭 {ev.title}{who}",
            'start': ev.date.isoformat(),
            'backgroundColor': '#a2d2ff', 
            'borderColor': '#7fb3e6',
            'extendedProps': {
                'type': 'event'
            }
        })

    apps = Application.objects.filter(status='approved').exclude(event_date__isnull=True).exclude(event_time__isnull=True)
    for ap in apps:
        assign = Assignment.objects.filter(application=ap).first()
        
        if assign:
            if assign.group:
                who = f" — [{assign.group.name}]"
            elif assign.staff:
                who = f" — [{assign.staff.full_name}]"
            else:
                who = " — [Не назначен]"
        else:
            who = ""
        
        start_dt = datetime.combine(ap.event_date, ap.event_time)
        is_bday = ap.category == 'birthday'
        color = '#ff8b94' if is_bday else '#a8e6cf'
        icon = '🎂' if is_bday else '🎓'
        data.append({
            'id': f"ap{ap.id}",
            'title': f"{icon} {ap.full_name}{who}",
            'start': start_dt.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'type': 'application'  
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

    @action(detail=True, methods=['get'])
    def busy_dates(self, request, pk=None):
        staff = self.get_object()
        assignments = Assignment.objects.filter(
            Q(staff=staff) | Q(group__members=staff)
        ).distinct()

        events = []
        for a in assignments:
            try:
                if a.application:
                    if not a.application.event_date or not a.application.event_time: continue
                    start_dt = datetime.combine(a.application.event_date, a.application.event_time)
                    title = f"Заказ: {a.application.full_name}"
                    color = '#2ec4b6'
                elif a.event:
                    if not a.event.date: continue
                    start_dt = a.event.date
                    title = f"Спектакль: {a.event.title}"
                    color = '#ff9f43'
                else: continue

                events.append({
                    'title': title,
                    'start': start_dt.isoformat(),
                    'end': (start_dt + timedelta(hours=2)).isoformat(),
                    'allDay': False,
                    'backgroundColor': color,
                    'borderColor': color,
                })
            except Exception: continue
        return Response(events)

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        
        app_id = data.get('application')
        event_id = data.get('event')
        staff_id = data.get('staff') or None
        group_id = data.get('group') or None
        
        try:
            assignment_instance = Assignment(
                application_id=app_id,
                event_id=event_id,
                staff_id=staff_id,
                group_id=group_id
            )
            assignment_instance.clean()
        except ValidationError as e:
            error_text = e.message if hasattr(e, 'message') else str(e.messages[0])
            return Response({
                'status': 'warning',
                'message': error_text
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'status': 'warning',
                'message': f"Системная ошибка проверки: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('dry_run'):
            return Response({"status": "available"}, status=status.HTTP_200_OK)

        with transaction.atomic():
            if app_id:
                Assignment.objects.filter(application_id=app_id).delete()
            elif event_id:
                Assignment.objects.filter(event_id=event_id).delete()

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class StaffGroupViewSet(viewsets.ModelViewSet):
    queryset = StaffGroup.objects.all()
    serializer_class = StaffGroupSerializer
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        event_date = request.query_params.get('event_date')
        event_time = request.query_params.get('event_time')
        app_id = request.query_params.get('application_id')
        event_obj_id = request.query_params.get('event_id')

        if (not event_date or not event_time) and app_id:
            try:
                app = Application.objects.get(id=app_id)
                event_date = app.event_date
                event_time = app.event_time
            except Application.DoesNotExist:
                pass
                
        if (not event_date or not event_time) and event_obj_id:
            try:
                ev = Event.objects.get(id=event_obj_id)
                if ev.date:
                    event_date = ev.date.date()
                    event_time = ev.date.time()
            except Event.DoesNotExist:
                pass

        if event_date and event_time:
            if hasattr(event_time, 'strftime'):
                event_time_str = event_time.strftime('%H:%M')
            else:
                event_time_str = str(event_time)[:5]

            busy_staff_q = Assignment.objects.filter(
                Q(application__event_date=event_date, application__event_time__contains=event_time_str) |
                Q(event__date__date=event_date, event__date__time__contains=event_time_str)
            )
            
            if app_id:
                busy_staff_q = busy_staff_q.exclude(application_id=app_id)
            if event_obj_id:
                busy_staff_q = busy_staff_q.exclude(event_id=event_obj_id)

            busy_staff_ids = busy_staff_q.values_list('staff_id', flat=True).distinct()

            custom_data = []
            for group in queryset:
                member_objects = group.members.all()
                group_members_info = []
                has_busy_members = False

                for member in member_objects:
                    is_busy = member.id in busy_staff_ids
                    if is_busy:
                        has_busy_members = True
                    
                    group_members_info.append({
                        'id': member.id,
                        'full_name': member.full_name,
                        'is_busy': is_busy
                    })

                custom_data.append({
                    'id': group.id,
                    'name': group.name,
                    'has_busy_members': has_busy_members,
                    'members': group_members_info
                })
            return Response(custom_data)

        custom_data = []
        for group in queryset:
            custom_data.append({
                'id': group.id,
                'name': group.name,
                'has_busy_members': False,
                'members': [{'id': m.id, 'full_name': m.full_name, 'is_busy': False} for m in group.members.all()]
            })
        return Response(custom_data)

class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer