from django.urls import path
from . import views

urlpatterns = [
    path('bookingPage/', views.bookingPage, name='bookingPage'),
    path('bookingCheck/', views.bookingCheck, name='bookingCheck'),
    path('bookingPayment/', views.bookingPayment, name='bookingPayment'),
    path('bookingSuccess/', views.bookingSuccess, name='bookingSuccess'),
    path('profile/<str:pk>', views.patientProfile, name='profile'),
    path('profile-history/<str:pk>', views.patientHistory, name='history'),
    path('profile-payment/<str:pk>', views.paymentHistory, name='payment'),
    path('doctor-profile/<str:pk>', views.doctorProfile, name='doctorProfile'),
    path('doctor-work/<str:pk>', views.doctorWork, name='doctorWork'),
    path('appointment-detail/<str:pk>', views.appointmentDetail, name='appointmentDetail'),
    path('supportPage/', views.supportPage, name='supportPage'),
    
]