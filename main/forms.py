from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'phone', 'email', 'age', 'address', 'event_date_time', 'tariff']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше ФИО'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@mail.ru'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Возраст'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес проведения'}),
            'event_date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'tariff': forms.Select(attrs={'class': 'form-control'}),
        }