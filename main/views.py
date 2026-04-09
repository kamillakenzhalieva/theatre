from django.shortcuts import render
from .models import Event
from .forms import ApplicationForm
from .models import Tariff
from .models import Application
from django.shortcuts import redirect

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def afisha(request):
    mock_events = [
        {
            'title': 'Три поросенка',
            'date': '12 апреля, 12:00',
            'location': 'Большой зал',
            'description': 'Классическая сказка в интерактивном формате. Малыши помогут строить домики и спасаться от волка!',
            'price': '800',
            'ticket_link': '#'
        },
        {
            'title': 'Тайна старого шкафа',
            'date': '19 апреля, 16:00',
            'location': 'Камерная сцена',
            'description': 'Волшебная история о дружбе и храбрости. Зрителей ждут световые эффекты и чудеса.',
            'price': '1200',
            'ticket_link': '#'
        }
    ]
    return render(request, 'afisha.html', {'events': mock_events})

def birthdays(request):
    mock_packages = [
        {
            'title': 'Пакет «Стандарт»',
            'description': 'Аренда зала на 2 часа, интерактивная сказка, поздравление от героя и чаепитие.',
            'price': '15 000',
            'features': ['До 10 детей', '1 аниматор', 'Базовый декор']
        },
        {
            'title': 'Пакет «Премиум»',
            'description': 'Аренда на 3 часа, расширенный спектакль, шоу мыльных пузырей и тематическая фотозона.',
            'price': '25 000',
            'features': ['До 20 детей', '2 аниматора', 'Шоу-программа']
        }
    ]
    return render(request, 'birthdays.html', {'packages': mock_packages})

def birthday_page(request):
    form = ApplicationForm()
    form.fields['tariff'].queryset = Tariff.objects.filter(service__category='birthday')    
    return render(request, 'birthdays.html', {'form': form})

def spectacles_view(request):
    events = Event.objects.all()
    return render(request, 'spectacles.html', {'events': events})

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
        
        full_comment = f"Услуга: {selection}. Возраст: {age_range}. Время: {event_time}. \nКомментарий: {comment}"

        Application.objects.create(
            category='birthday' if category == 'День Рождения' else 'graduation' if category == 'Выпускной' else 'spectacle',
            full_name=full_name, 
            phone=phone,
            email=email,
            age=5, 
            address=address,
            event_date_time=f"{event_date} 12:00", 
            comment=full_comment
        )
        return redirect('home') 
    return redirect('home')

def graduation_view(request):
    tariffs = Tariff.objects.filter(service__category='graduation')
    return render(request, 'graduation.html', {'tariffs': tariffs})