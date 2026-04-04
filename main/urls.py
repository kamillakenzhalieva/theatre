from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('afisha/', views.afisha, name='afisha'),
    path('about/', views.about, name='about'),
    path('birthdays/', views.birthdays, name='birthdays'),
]