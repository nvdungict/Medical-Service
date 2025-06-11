import json
import random
import string
import django
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.db.models import Q,Count, Sum, F
from django.db import models
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse

from service.models import Appointment, Doctor, Patient, Room, Service
from user.models import User
from .forms import MyUserCreationForm
from django.contrib.auth.decorators import login_required

from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta

def admin(request):
    doctors_count = Doctor.objects.all().count()
    patients_count = Patient.objects.all().count()
    finished_appointment = Appointment.objects.filter(status=1).count()
    pending_appointment = Appointment.objects.filter(status=2).count()
    appointments = Appointment.objects.all().order_by('-appointment_date')[:30]

    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    sale_last_month = Service.objects.filter(appointment__created__gte=one_month).aggregate(total_sales=models.Sum('price'))
    sale_two_month = Service.objects.filter(Q(appointment__created__lt=one_month) & Q(appointment__created__gte=two_month)).aggregate(total_sales=models.Sum('price'))
    sale_three_month = Service.objects.filter(Q(appointment__created__lt=two_month) & Q(appointment__created__gte=three_month)).aggregate(total_sales=models.Sum('price'))
    sale_four_month = Service.objects.filter(Q(appointment__created__lt=three_month) & Q(appointment__created__gte=four_month)).aggregate(total_sales=models.Sum('price'))
    if sale_last_month['total_sales'] == None:
        sale_last_month['total_sales'] = 0
    if sale_two_month['total_sales'] == None:
        sale_two_month['total_sales'] = 0
    if sale_three_month['total_sales'] == None:
        sale_three_month['total_sales'] = 0
    if sale_four_month['total_sales'] == None:
        sale_four_month['total_sales'] = 0
    if sale_four_month['total_sales'] != 0:
        percent1 = sale_last_month['total_sales']/sale_four_month['total_sales']*15
        percent2 = sale_two_month['total_sales']/sale_four_month['total_sales']*15
        percent3 = sale_three_month['total_sales']/sale_four_month['total_sales']*15
        percent4 = sale_four_month['total_sales']/sale_four_month['total_sales']*15
    else:
        percent1 = 0
        percent2 = 0
        percent3 = 0
        percent4 = 0
    
    if request.method == 'POST':
        value = request.POST.get('filter')
        appointments = Appointment.objects.filter(Q(status__startswith=value) | Q(start_time__icontains=value)
                                                  | Q(status__icontains=value) | Q(start_time__startswith=value)
                                                  | Q(appointment_date__icontains=value) | Q(appointment_date__startswith=value))[:30]


    context =   {
                    "doctors_count": doctors_count,
                    "patients_count": patients_count,
                    "finished_appointment": finished_appointment,
                    "pending_appointment": pending_appointment,
                    "appointments": appointments,
                    "sale_last_month": sale_last_month,
                    "sale_two_month": sale_two_month,
                    "sale_three_month": sale_three_month,
                    "sale_four_month": sale_four_month,
                    "one_month": one_month ,
                    "two_month": two_month ,
                    "three_month": three_month,
                    "four_month":  four_month,
                    "percent1":  percent1,
                    "percent2":  percent2,
                    "percent3":  percent3,
                    "percent4":  percent4,
                }
    return render(request, 'admin/admin.html', context)

def adminDoctor(request):
    doctors = Doctor.objects.all()[:30]
    doctors_count = Doctor.objects.all().count()
    doctors_active = Doctor.objects.filter(status=1).count()
    doctors_unactive = doctors_count - doctors_active
    services = Service.objects.all()
    service_count = Service.objects.annotate(total=Count('doctor')).values('service_name', 'total')
    specialize_count = []

    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            doctors = Doctor.objects.all()[:30]
        elif request.POST.get('working') == 'working':
            doctors = Doctor.objects.all().filter(status=1)[:30]
        elif request.POST.get('not') == 'not':
            doctors = Doctor.objects.all().filter(status=2)[:30]
        else:
            value = request.POST.get('filter')
            doctors = Doctor.objects.filter(Q(firstname__startswith=value) | Q(firstname__icontains=value)
                                              |Q(lastname__startswith=value) |Q(lastname__contains=value))

    for doctor in doctors:
        specialize_count.append(Doctor.objects.filter(doctor_id=doctor.doctor_id).annotate(total=Count('service')).values('doctor_id','total')) 
    
    context = {
        "doctors":doctors,
        "doctors_count":doctors_count,
        "doctors_active":doctors_active,
        "doctors_unactive":doctors_unactive,
        "services":services,
        "service_count":service_count,
        "specialize_count":specialize_count,
    }

    return render(request, 'admin/admin_doctor.html', context)

def adminPatient(request):
    patients = Patient.objects.all()[:30]
    patient_payment = []
    booking_numbers = []
    total_payment = Appointment.objects.filter(patient__isnull=False).aggregate(Sum('service__price'))['service__price__sum'] or 0

    gold  = Patient.objects.select_related('membership').filter(membership_id='3').count()
    silver  = Patient.objects.select_related('membership').filter(membership_id='2').count()
    bronze  = Patient.objects.select_related('membership').filter(membership_id='1').count()

    
    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            patients = Patient.objects.all().order_by('patient_id')[:30]
        elif request.POST.get('a') == 'a':
            patients = Patient.objects.select_related('membership').filter(membership_id='3')[:30]
        elif request.POST.get('b') == 'b':
            patients = Patient.objects.select_related('membership').filter(membership_id='2')[:30]
        elif request.POST.get('c') == 'c':
            patients = Patient.objects.select_related('membership').filter(membership_id='1')[:30]
        else:
            value = request.POST.get('filter')
            patients = Patient.objects.filter(Q(firstname__startswith=value) | Q(firstname__icontains=value)
                                              |Q(lastname__startswith=value) |Q(lastname__contains=value))[:30]

    for patient in patients:
        patient_payment.append(Appointment.objects.filter(patient_id=patient.patient_id).aggregate(total_payment=models.Sum('service__price'))['total_payment'] or 0)  
        booking_numbers.append(Appointment.objects.filter(patient_id=patient.patient_id).aggregate(total_booking=models.Count('appointment_id'))['total_booking'] or 0)
    
    patients_count = Patient.objects.all().count()
    context = {
        "patients": patients,
        "patients_count": patients_count,
        "patient_payment": patient_payment,
        "booking_numbers": booking_numbers,
        "gold": gold,
        "silver": silver,
        "bronze": bronze,
    }
    return render(request, 'admin/admin_patient.html', context)

def adminAppointment(request):
    appointments = Appointment.objects.all()[:30]
    appointment_count = Appointment.objects.all().count()
    appointment_finished = Appointment.objects.filter(status=1).count()
    appointment_processing = Appointment.objects.filter(status=2).count()
    appointment_pending = Appointment.objects.filter(status=3).count()


    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    order_last_month = Appointment.objects.filter(created__gte=one_month).aggregate(total_order=models.Count('*'))
    order_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month)).aggregate(total_order=models.Count('*'))
    order_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month)).aggregate(total_order=models.Count('*'))
    order_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month)).aggregate(total_order=models.Count('*'))
    
    if order_four_month['total_order'] != 0:
        percent1 = order_last_month['total_order']/order_four_month['total_order']*15
        percent2 = order_two_month['total_order']/order_four_month['total_order']*15
        percent3 = order_three_month['total_order']/order_four_month['total_order']*15
        percent4 = order_four_month['total_order']/order_four_month['total_order']*15
    else:
        percent1 = 0
        percent2 = 0
        percent3 = 0
        percent4 = 0

    if request.method == 'POST':
        if request.method == 'POST':
            if request.POST.get('all') == 'all':
                appointments = Appointment.objects.all()[:30]
            elif request.POST.get('f') == 'f':
                appointments = Appointment.objects.filter(status=1)[:30]
            elif request.POST.get('p') == 'p':
                appointments = Appointment.objects.filter(status=2)[:30]
            elif request.POST.get('pen') == 'pen':
                appointments = Appointment.objects.filter(status=3)[:30]
            else:
                value = request.POST.get('filter')
                appointments = Appointment.objects.select_related('patient').filter(Q(appointment_id=value))[:30]

    context = {
        'appointments':appointments,
        'appointment_finished':appointment_finished,
        'appointment_processing':appointment_processing,
        'appointment_pending':appointment_pending,
        'appointment_count':appointment_count,
        'percent1':percent1,
        'percent2':percent2,
        'percent3':percent3,
        'percent4':percent4,
        "order_last_month": order_last_month,
        "order_two_month": order_two_month,
        "order_three_month": order_three_month,
        "order_four_month": order_four_month,
        "one_month": one_month ,
        "two_month": two_month ,
        "three_month": three_month,
        "four_month":  four_month,
    }
    return render(request, 'admin/admin_appoinment.html', context)

def adminRoom(request):
    rooms = Room.objects.all()
    room_count = Room.objects.all().count()
    room_free = Room.objects.filter(status=1).count()
    room_inused = Room.objects.filter(status=2).count()
    room_stopped = Room.objects.filter(status=3).count()

    room_free__deg = (room_free / room_count) *360
    room_inused__deg = room_free__deg + (room_inused / room_count)*360
    room_stopped__deg = room_inused__deg + (room_stopped / room_count)*360

    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            rooms = Room.objects.all()  
        elif request.POST.get('1') == '1':
            rooms = Room.objects.filter(status=1)
        elif request.POST.get('2') == '2':
            rooms = Room.objects.filter(status=2)
        elif request.POST.get('3') == '3':
            rooms = Room.objects.filter(status=3)
        else:
            value = request.POST.get('filter')
            rooms = Room.objects.filter(Q(room_name__contains=value) | Q(room_name__startswith=value)
                                            | Q(room_id__contains=value) | Q(room_id__startswith=value))[:4]

    context = {
        'rooms': rooms,
        'room_count': room_count,
        'room_free': room_free,
        'room_inused': room_inused,
        'room_stopped': room_stopped,
        'room_free__deg': room_free__deg,
        'room_inused__deg': room_inused__deg,
        'room_stopped__deg': room_stopped__deg,
    }
    return render(request, 'admin/admin_room.html', context)

def adminService(request):
    services = Service.objects.all()
    total = Service.objects.all().count()
    service_running = Service.objects.filter(status=1).count()
    service_freezed = Service.objects.filter(status=2).count()
    service_pending = Service.objects.filter(status=3).count()


    if request.method == 'POST':
        if request.POST.get('all') == 'all':
            services = Service.objects.all()
        elif request.POST.get('running') == 'running':
            services = Service.objects.filter(status=1)
        elif request.POST.get('freezed') == 'freezed':
            services = Service.objects.filter(status=2)
        elif request.POST.get('pending') == 'pending':
            services = Service.objects.filter(status=3)
        else:
            value = request.POST.get('filter')
            services = Service.objects.filter(Q(service_name__contains=value) | Q(service_name__startswith=value)
                                         | Q(service_id__contains=value) | Q(service_id__startswith=value))[:4]

    context = {
        'total': total,
        'service_running': service_running,
        'service_freezed': service_freezed,
        'service_pending': service_pending,
        'services': services,
    }
    return render(request, 'admin/admin_service.html', context)


def adminRoomDetail(request, pk):
    room = Room.objects.get(room_id=pk)

    rooms = Room.objects.all()
    room_count = Room.objects.all().count()
    room_free = Room.objects.filter(status=1).count()
    room_inused = Room.objects.filter(status=2).count()
    room_stopped = Room.objects.filter(status=3).count()

    lastest_appointment = Appointment.objects.filter(room_id=room.room_id).values('start_time', 'appointment_date').order_by('-appointment_date', '-start_time')[0]
    
    context = {
        'room_count': room_count,
        'room_free': room_free,
        'room_inused': room_inused,
        'room_stopped': room_stopped,
        'room':room,
        'lastest_appointment':lastest_appointment,
    }
    return render(request, 'admin/admin_roomDetail.html', context)

def supportPage(request):
    time_now = datetime.now()
    return render(request, 'admin/support_page.html', {'time_now': time_now,})

def serviceDetail(request, pk):
    service = Service.objects.get(service_id=pk)
    total = Service.objects.all().count()
    service_running = Service.objects.filter(status=1).count()
    service_freezed = Service.objects.filter(status=2).count()
    service_pending = Service.objects.filter(status=3).count()

    one_month = timezone.now() - timedelta(days=30)
    two_month = timezone.now() - timedelta(days=60)
    three_month = timezone.now() - timedelta(days=90)
    four_month = timezone.now() - timedelta(days=120)
    total_order = Appointment.objects.filter(Q(service=service)).aggregate(total_order=models.Count('*'))['total_order']
    order_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    order_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_order=models.Count('*'))
    
    if order_four_month['total_order'] != 0:
        percent1 = order_last_month['total_order']/order_four_month['total_order']*15
        percent2 = order_two_month['total_order']/order_four_month['total_order']*15
        percent3 = order_three_month['total_order']/order_four_month['total_order']*15
        percent4 = order_four_month['total_order']/order_four_month['total_order']*15
    else:
        percent1 = 10
        percent2 = 10
        percent3 = 10
        percent4 = 10
    
    total_income = Appointment.objects.filter(Q(service=service)).aggregate(total_income=models.Sum('service__price'))['total_income']
    income_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))
    income_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_income=models.Sum('service__price'))

    if order_four_month['total_order'] != 0:
        percent_1 = income_last_month['total_income']/income_four_month['total_income']*15
        percent_2 = income_two_month['total_income']/income_four_month['total_income']*15
        percent_3 = income_three_month['total_income']/income_four_month['total_income']*15
        percent_4 = income_four_month['total_income']/income_four_month['total_income']*15
    else:
        percent_1 = 10
        percent_2 = 10
        percent_3 = 10
        percent_4 = 10
     
    context = {
        'service':service,
        'total':total,
        'service_running':service_running,
        'service_freezed': service_freezed,
        'service_pending': service_pending,
        'percent1':percent1,
        'percent2':percent2,
        'percent3':percent3,
        'percent4':percent4,
        "order_last_month": order_last_month,
        "order_two_month": order_two_month,
        "order_three_month": order_three_month,
        "order_four_month": order_four_month,
        "one_month": one_month ,
        "two_month": two_month ,
        "three_month": three_month,
        "four_month":  four_month,
        "total_order":  total_order,
        "income_last_month":  income_last_month,
        "income_two_month":  income_two_month,
        "income_three_month":  income_three_month,
        "income_four_month":  income_four_month,
        "percent_1":  percent_1,
        "percent_2":  percent_2,
        "percent_3":  percent_3,
        "percent_4":  percent_4,
        "total_income":  total_income,
    }
    return render(request, 'service/service_detail.html', context)

def adminAdd(request):
    if request.method == 'POST':
        form_data = request.POST
        email = form_data['email']
        username = form_data['username']
        password1 = form_data['password1']
        password2 = form_data['password2']

        user_form = {'email': email, 'username': username, 'password1': password1, 'password2': password2}
        service_ids = form_data.get('services')
        if service_ids:
            service_ids = service_ids.split(',')
            service_ids = list(service_ids)
            print(service_ids)
            form = MyUserCreationForm(user_form)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.username.lower()
                user.role = "DOCTOR"
                user.save()

                services = Service.objects.filter(service_id__in=service_ids)
                print(services)
                doctor = Doctor.objects.create(doctor_id=''.join(random.choices(string.ascii_letters + string.digits, k=8)),user=user)
                doctor.service.set(services)
                print(doctor)
                
                try:
                    doctor.save()
                except django.db.utils.IntegrityError as e:
                    print(e)
                return JsonResponse({'success': True})
            else:
                print("hello")
                errors = form.errors.as_json()
                return JsonResponse({'success': False, 'errors': errors})
        else:
            return JsonResponse({'success': False, 'message': 'Check services'})
    else:
        form = MyUserCreationForm()
        services = Service.objects.all()
        context = {'form': form, 'services': services}
        return render(request, 'admin/admin_doctor.html', context)