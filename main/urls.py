from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('afisha/', views.afisha, name='afisha'),
    path('about/', views.about, name='about'),
    path('birthdays/', views.birthdays, name='birthdays'),
    path('spectacles/', views.spectacles_view, name='spectacles_page'),
    path('apply/', views.application_view, name='application_page'),
]