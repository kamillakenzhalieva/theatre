from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'home', views.HomePageViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'tariffs', views.TariffViewSet)
router.register(r'applications', views.ApplicationViewSet)
router.register(r'entertainment', views.EntertainmentItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),

    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('afisha/', views.afisha, name='afisha'),
    path('spectacles/', views.spectacles_view, name='spectacles_page'),
    path('spectacles/<int:pk>/', views.event_detail, name='event_detail'),
    path('birthdays/', views.birthday_page, name='birthdays'),
    path('graduation/', views.graduation_view, name='graduation_page'),
    path('apply/', views.ApplicationViewSet.as_view({'post': 'create'}), name='application_page'),
    
    path('management/', views.admin_panel, name='admin_panel'),
    path('api/calendar-data/', views.calendar_events_api, name='calendar_data'),
    path('calendar-page/', views.calendar_page_render),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)