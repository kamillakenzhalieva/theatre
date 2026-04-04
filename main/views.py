from django.shortcuts import render
from .models import Event

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def afisha(request):
    events = Event.objects.all()
    return render(request, 'afisha.html', {'events': events})