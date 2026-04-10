from django.shortcuts import render, get_object_or_404, redirect
from .models import Event, Tariff, Application
from .forms import ApplicationForm
from django.utils import timezone

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')


def spectacles_view(request):
    events = Event.objects.filter(is_active=True).order_by('date')
    return render(request, 'spectacles.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'event_detail.html', {'event': event})


def birthday_page(request):
    tariffs = Tariff.objects.filter(service__category='birthday')
    form = ApplicationForm()
    
    if 'tariff' in form.fields:
        form.fields['tariff'].queryset = tariffs
    return render(request, 'birthdays.html', {'form': form, 'tariffs': tariffs})


def graduation_view(request):
    tariffs = Tariff.objects.filter(service__category='graduation')
    return render(request, 'graduation.html', {'tariffs': tariffs})


def application_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        category = request.POST.get('category')  
        age_range = request.POST.get('age_range')
        selection = request.POST.get('selection') 
        address = request.POST.get('address')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        comment = request.POST.get('comment')
        
       
        cat_map = {
            'День Рождения': 'birthday',
            'Выпускной': 'graduation',
            'Спектакль': 'spectacle'
        }
        db_category = cat_map.get(category, 'spectacle')

        
        if event_date:
            dt_string = f"{event_date} {event_time if event_time else '00:00'}"
        else:
            dt_string = timezone.now() 

     
        Application.objects.create(
            category=db_category,
            full_name=full_name, 
            phone=phone,
            email=email,
            age=age_range if age_range else "Не указан", 
            address=address if address else "В театре",
            event_date_time=dt_string,
            
        )
        return redirect('home') 
    return redirect('home')

def afisha(request):
    events = Event.objects.all()
    return render(request, 'afisha.html', {'events': events})