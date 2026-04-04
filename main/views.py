from django.shortcuts import render
from .models import Event

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