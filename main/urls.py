from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('spectacles/', views.spectacles_view, name='spectacles_page'),
    path('spectacles/<int:pk>/', views.event_detail, name='event_detail'),
    path('birthdays/', views.birthday_page, name='birthdays'),
    path('graduation/', views.graduation_view, name='graduation_page'),
    path('apply/', views.application_view, name='application_page'),
    path('about/', views.about, name='about'),
    path('afisha/', views.afisha, name='afisha'),
]