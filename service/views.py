from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Service, Appointment, Room, Doctor, Patient
from payment.models import Payment
from user.models import User
from datetime import datetime, timedelta
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser

# Create your views here.
def bookingPage(request):
    if request.user.is_authenticated:
        service_count = Service.objects.annotate(total=Count('doctor')).values('service_id', 'service_name', 'total')
        user = User.objects.get(id=request.user.id)
        current_date = datetime.now().strftime('%Y-%m-%d')
        next_year = (timedelta(days=365) + datetime.now()).strftime('%Y-%m-%d')

        if request.method == 'POST':
            date = request.POST.get('date')
            time = request.POST.get('time')
            email = request.POST.get('email')
            service_id = request.POST.get('service')
            symptoms = request.POST.get('textarea')
            service = Service.objects.get(service_id=service_id)

            # Convert date and time to datetime objects for comparison
            appointment_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')

            # Check doctor availability for the given service and time
            available_doctors = Doctor.objects.filter(service=service)
            conflicting_appointments = Appointment.objects.filter(
                doctor__in=available_doctors,
                appointment_date=appointment_datetime.date(),
                start_time=appointment_datetime.time()
            )
            print(available_doctors)
            if not available_doctors:
                print("none")
            if conflicting_appointments.exists() or not available_doctors:
                context = {
                    "service_count": service_count,
                    "user": user,
                    "current_date": current_date,
                    "next_year": next_year,
                    "error_message": "No doctor is available at the selected date and time."
                }
                return render(request, 'service/booking_page.html', context)
            else:
                context = {
                    "date": date,
                    "time": time,
                    "email": email,
                    "service": service,
                    "symptoms": symptoms,
                }

                booking_info = {
                    "date": date,
                    "time": time,
                    "email": email,
                    "service_name": service.service_name,
                    "service_id": service.service_id,
                    "service_price": float(service.price),
                    "symptoms": symptoms,
                }
                request.session['booking_info'] = booking_info
                return redirect('bookingCheck')
        else:
            context = {
                "service_count": service_count,
                "user": user,
                "current_date": current_date,
                "next_year": next_year,
            }
            return render(request, 'service/booking_page.html', context)
    else:
        return redirect('login')

def bookingCheck(request):
    if request.user.is_authenticated:
        booking_info = request.session.get('booking_info', None)
        print(booking_info)
        service = Service.objects.filter(service_name=booking_info['service_name'])
        print(service[0].service_name)
        doctor = Doctor.objects.filter(Q(status=1) & Q(service=service[0]))[:1]
        print(doctor[0].user)
        room = Room.objects.filter(status=1)[:1]
        if request.method == 'POST':
            print(booking_info)
            new_appointment = Appointment.objects.create(appointment_date=booking_info['date'],
                                        start_time=booking_info['time'],
                                        status=3,
                                        doctor=doctor[0],
                                        patient=request.user.patient,
                                        service=service[0],
                                        room_id=room[0],
                                        ).appointment_id
            room[0].status = 2
            doctor[0].status = 2
            doctor[0].save()
            room[0].save()
            request.session['appointment_id'] = new_appointment
            request.session.save()
            return redirect('bookingPayment')
        print(booking_info['service_name'])
        return render(request, 'service/booking_check.html',booking_info)
    else:
        return redirect('login')
   

def bookingPayment(request):
    if request.user.is_authenticated:
        booking_info = request.session.get('booking_info', None)
        print(booking_info)
        service_name = booking_info['service_name']
        price = Service.objects.filter(service_id=booking_info['service_id']).values('price')[0]['price']
        membership = Patient.objects.filter(user__email=booking_info['email'])[0].membership
        membership_type = membership.type
        membership_percent = membership.discount_percent
        discount = int(price)*membership_percent/100.0 
        vat = int(price) * 0.05
        bill = int(price) + vat - discount
        print(membership)
        context = {
            'price': price,
            'membership_type': membership_type,
            'discount': discount,
            'vat': vat,
            'bill': bill,
            'service_name': service_name,
        }
        appointment = Appointment.objects.filter(appointment_id=request.session.get('appointment_id'))[0]
        Payment.objects.create(appointment_id=appointment, status=0)
        return render(request, 'service/booking_payment.html', context)
    else:
        return redirect('login')

def bookingSuccess(request):
    if request.user.is_authenticated:
        appointment_id = request.session['appointment_id']
        return render(request, 'service/booking_success.html', {'appointment_id':appointment_id})
    else:
        return redirect('login')

@login_required(login_url='login')    
def patientProfile(request, pk):
    time_now = datetime.now()
    edit = False
    edit_2 = False
    user = User.objects.get(id=pk)
    patient = Patient.objects.get(user_id=request.user.id)
    lastname = patient.lastname or ''
    contact_number = patient.contact_number or ''
    cccd = patient.cccd
    firstname = patient.firstname or ''
    address = patient.address or ''
    dob = patient.dob or ''
    bmi = patient.bmi or ''
    weight = patient.weight or ''
    height = patient.height or ''
    bloodpressure = patient.blood_pressure or ''
    gender = patient.gender or 1
    email = request.user.email 

    print(1)

    if request.user.is_authenticated:
        if request.POST.get('value') == 'edit':
            edit = True
        else:
            edit = False
            if request.POST.get('value') == 'save':
                gender = int(request.POST.get('gender'))
                address = request.POST.get('address') 
                dob = request.POST.get('dob') 
                bmi = request.POST.get('bmi') 
                weight = request.POST.get('weight') 
                height = request.POST.get('height') 
                bloodpressure = request.POST.get('bloodpressure')
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                patient.address = address
            if dob == "" :
                    dob = '2004-01-01'
            patient.dob = dob
            if bmi == "" :
                    bmi = None
            patient.bmi = bmi
            if weight == "" :
                    weight = None
            patient.weight = weight
            if height == "" :
                    height = None
            patient.height = height
            if bloodpressure == "" :
                    bloodpressure = None
            patient.blood_pressure = bloodpressure
            user.first_name = firstname
            user.last_name = lastname
            patient.firstname = firstname
            patient.lastname = lastname
            patient.save()
            user.save()

        if request.POST.get('value') == 'edit_2':
            edit_2 = True
        else:
            edit_2 = False
            if request.POST.get('value') == 'save_2':
                contact_number = request.POST.get('contact_number')
                email = request.POST.get('email')
                cccd = request.POST.get('cccd')
                address = request.POST.get('address')
                patient.contact_number = contact_number
                patient.address = address
                patient.cccd  = cccd 
                patient.save()
        
        appointments = Appointment.objects.filter(patient=patient).order_by('appointment_date').all()[:30] or ''

        context = { 'gender':gender,
                    'user':user,
                    'edit':edit,
                    'edit_2':edit_2,
                    'lastname':lastname,
                    'firstname':firstname,
                    'address':address,
                    'contact_number':contact_number,
                    'cccd': cccd,
                    'dob':dob,
                    'bmi':bmi,
                    'weight':weight,
                    'height':height,
                    'bloodpressure': bloodpressure,
                    'email': request.user.email,
                    'appointments': appointments,
                    'time_now': time_now,
                }
        
        return render(request, 'service/patient_profile.html', context)
    else:
        return redirect('login')
    
@login_required(login_url='login')
def patientHistory(request,pk):
    if request.user.is_authenticated:
        patient = Patient.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(patient=patient).all()[:30] or ''

        if request.method == 'POST':
            date = request.POST.get('date')
            if date != "":
                appointments = Appointment.objects.filter(Q(appointment_date=date) & Q(patient=patient))[:30] or ''

        context = {
            'appointments': appointments
        }
        return render(request, 'service/patient_history.html', context)
    else:
        return redirect('login')
    

@login_required(login_url='login')    
def doctorProfile(request, pk):
    
    edit = False
    edit_2 = False
    user = User.objects.get(id=pk)
    doctor = Doctor.objects.get(user_id=request.user.id)
    dob = doctor.dob or ''
    lastname = doctor.lastname or ''
    contact_number = doctor.contact_number or ''
    cccd = doctor.cccd
    firstname = doctor.firstname or ''
    address = doctor.address or ''
    gender = doctor.gender or 1
    email = request.user.email 
    services = doctor.service.all()

    if request.user.is_authenticated:
        if request.POST.get('value') == 'edit':
            edit = True
        else:
            edit = False
            if request.POST.get('value') == 'save':
                gender = int(request.POST.get('gender'))
                address = request.POST.get('address') 
                dob = request.POST.get('dob') 
                firstname = request.POST.get('firstname')
                lastname = request.POST.get('lastname')
                doctor.address = address
            if dob == "" :
                dob = None
            if address == "" :
                address = None
            if firstname == "" :
                firstname = None
            if lastname == "" :
                lastname = None

            user.first_name = firstname
            user.last_name = lastname
            doctor.firstname = firstname
            doctor.lastname = lastname
            doctor.save()
            user.save()

        if request.POST.get('value') == 'edit_2':
            edit_2 = True
        else:
            edit_2 = False
            if request.POST.get('value') == 'save_2':
                contact_number = request.POST.get('contact_number')
                email = request.POST.get('email')
                cccd = request.POST.get('cccd')
                address = request.POST.get('address')
                doctor.contact_number = contact_number
                doctor.address = address
                doctor.cccd  = cccd 
                doctor.save()
        
        appointments = Appointment.objects.filter(doctor=doctor).all()[:30] or ''

        context = { 'gender':gender,
                    'user':user,
                    'edit':edit,
                    'edit_2':edit_2,
                    'lastname':lastname,
                    'firstname':firstname,
                    'address':address,
                    'contact_number':contact_number,
                    'cccd': cccd,
                    'dob':dob,
                    'email': request.user.email,
                    'appointments': appointments,
                    'doctor':doctor,
                    'services': services
                }
        
        return render(request, 'service/doctor_profile.html', context)
    else:
        return redirect('login')


@login_required(login_url='login')
def doctorWork(request, pk):
    if request.user.is_authenticated:
        doctor = Doctor.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(doctor=doctor).all()[:30] or ''

        if request.method == 'POST':
            date = request.POST.get('date')
            if date != "":
                appointments = Appointment.objects.filter(Q(appointment_date=date) & Q(doctor=doctor))[:30] or ''

        context = {
            'appointments': appointments
        }
        return render(request, 'service/doctor_work.html', context)
    else:
        return redirect('login')

@login_required(login_url='login')   
def paymentHistory(request, pk):
    if request.user.is_authenticated:
        patient = Patient.objects.get(user_id=pk)
        appointments = Appointment.objects.filter(patient=patient).all()[:30] or ''

        if request.method == 'POST':
            payment_id = request.POST.get('id')
            if payment_id != '':
                appointments = Appointment.objects.filter(Q(appointment_id=payment_id) | Q(appointment_id__icontains=payment_id) & Q(patient=patient))[:30]

        context = {
            'appointments': appointments
        }
        return render(request, 'service/payment_history.html', context)
    else:
        return redirect('login')
    
#@login_required(login_url='login')    
def appointmentDetail(request,pk):
    if request.method == 'redirect':
        appointment_id = request.session['appointment_id']
    else:
        appointment_id = pk
    appointment = Appointment.objects.filter(appointment_id=appointment_id)[0]
    price = appointment.service.price
    membership_percent = appointment.patient.membership.discount_percent
    discount = int(price)*membership_percent/100.0 
    vat = int(price) * 0.05
    bill = int(price) + vat - discount

    context = { 
        'appointment':appointment,
        'discount': discount,
        'vat':vat,
        'bill':bill
    }
    if isinstance(request.user, AnonymousUser):
        if request.method == 'POST':
            if request.POST.get('finish') == "finish":
                appointment.status = 2
                appointment.save()
                return redirect('adminAppointment')
        return render(request, 'admin/appointment_detail.html', context)
    else:
        if request.method == 'POST':
            if request.POST.get('finish') == "finish":
                appointment.status = 1
                appointment.save()
                return redirect('doctorWork', pk=request.user.id)
                return redirect('adminAppointment')
        return render(request, 'service/appointment_detail.html', context)

def supportPage(request):
    time_now = datetime.now()
    return render(request, 'service/support_page.html', {'time_now': time_now,'user': request.user})

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
    total_order = Appointment.objects.filter(Q(service=service)).aggregate(total_order=Count('*'))['total_order']
    order_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_order=Count('*'))
    order_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_order=Count('*'))
    order_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_order=Count('*'))
    order_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_order=Count('*'))
    
    percent1 = order_last_month['total_order']/order_four_month['total_order']*15
    percent2 = order_two_month['total_order']/order_four_month['total_order']*15
    percent3 = order_three_month['total_order']/order_four_month['total_order']*15
    percent4 = order_four_month['total_order']/order_four_month['total_order']*15

    total_income = Appointment.objects.filter(Q(service=service)).aggregate(total_income=Sum('service__price'))['total_income']
    income_last_month = Appointment.objects.filter(Q(created__gte=one_month) & Q(service=service)).aggregate(total_income=Sum('service__price'))
    income_two_month = Appointment.objects.filter(Q(created__lt=one_month) & Q(created__gte=two_month) & Q(service=service)).aggregate(total_income=Sum('service__price'))
    income_three_month = Appointment.objects.filter(Q(created__lt=two_month) & Q(created__gte=three_month) & Q(service=service)).aggregate(total_income=Sum('service__price'))
    income_four_month = Appointment.objects.filter(Q(created__lt=three_month) & Q(created__gte=four_month) & Q(service=service)).aggregate(total_income=Sum('service__price'))

    percent_1 = income_last_month['total_income']/income_four_month['total_income']*15
    percent_2 = income_two_month['total_income']/income_four_month['total_income']*15
    percent_3 = income_three_month['total_income']/income_four_month['total_income']*15
    percent_4 = income_four_month['total_income']/income_four_month['total_income']*15

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


def telemedicine(request):
    return render(request, 'service/telemedicine.html')
    