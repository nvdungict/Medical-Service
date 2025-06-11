from django.urls import path, include
from allauth.socialaccount import providers

from user import views
# from service import views

urlpatterns = [
    path('', views.home, name='home'),
    path('developing/', views.developing, name='developing'),
    path('login/', views.loginPage, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('accounts/', include('allauth.urls')),
    
    path('telemedicine/', views.telemedicine, name='telemedicine'),
    path('records/', views.patient_records, name='patient_records'),
    path('calendar/', views.appointment_calendar, name='appointment_calendar'),
    #path('accounts/', include(providers.registry.get)),
]