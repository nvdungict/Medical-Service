from . import views
from django.urls import path
from django.urls import path, include
urlpatterns = [
    path('admin+/', views.admin, name='admin+'),
    path('adminDoctor/', views.adminDoctor, name='adminDoctor'),
    path('adminPatient/', views.adminPatient, name='adminPatient'),
    path('adminRoom/', views.adminRoom, name='adminRoom'),
    path('adminService/', views.adminService, name='adminService'),
    path('adminAppointment/', views.adminAppointment, name='adminAppointment'),
    path('adminService/serviceDetail/<str:pk>', views.serviceDetail, name='serviceDetail'),
    path('adminRoom/adminRoomDetail/<str:pk>', views.adminRoomDetail, name='adminRoomDetail'),
    path('adminDoctor/add', views.adminAdd, name='adminAdd'),
]