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
    tariffs = Tariff.objects.filter(category='birthday')
    packages = []
    for tariff in tariffs:
        packages.append({
            'title': tariff.name,
            'price': tariff.price,
            'features': [f.strip() for f in tariff.features_list.split('\n') if f.strip()],
        })
    form = ApplicationForm()
    if 'tariff' in form.fields:
        form.fields['tariff'].queryset = tariffs
    return render(request, 'birthdays.html', {'form': form, 'packages': packages})

def graduation_view(request):
    tariffs = Tariff.objects.filter(category='graduation')
    packages = []
    for tariff in tariffs:
        packages.append({
            'title': tariff.name,
            'price': tariff.price,
            'features': [f.strip() for f in tariff.features_list.split('\n') if f.strip()],
        })
    return render(request, 'graduation.html', {'packages': packages})

def application_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        category = request.POST.get('category')
        age_range = request.POST.get('age_range')
        address = request.POST.get('address')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        tariff_id = request.POST.get('tariff')

        cat_map = {
            'День Рождения': 'birthday',
            'Выпускной': 'graduation',
            'Спектакль': 'spectacle'
        }
        db_category = cat_map.get(category, 'spectacle')

        dt_string = f"{event_date} {event_time or '00:00'}" if event_date else timezone.now()

        Application.objects.create(
            category=db_category,
            full_name=full_name,
            phone=phone,
            email=email,
            age=age_range or "Не указан",
            address=address or "В театре",
            event_date_time=dt_string,
            tariff_id=tariff_id
        )
        return redirect('home')
    return redirect('home')

def afisha(request):
    events = Event.objects.all()
    return render(request, 'afisha.html', {'events': events})